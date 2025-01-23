#include "devtools.h"
#include <ppltasks.h>
#include <ShlObj.h>
#include <QWebSocket>
#include <QMetaEnum>
#include <QFileDialog>
#include <QMouseEvent>

extern const char *CHROME_LOCATION;
extern const char *START_DEVTOOLS;
extern const char *STOP_DEVTOOLS;
extern const char *HIDE_CHROME;
extern const char *DEVTOOLS_STATUS;
extern const char *AUTO_START;

extern const char *TRANSLATION_PROVIDER;

extern QFormLayout *display;
extern Settings settings;

namespace
{
	QLabel *statusLabel;
	AutoHandle<> process = NULL;
	QWebSocket webSocket;
	std::atomic<int> idCounter = 0;
	Synchronized<std::unordered_map<int, concurrency::task_completion_event<JSON::Value<wchar_t>>>> mapQueue;

	void StatusChanged(QString status)
	{
		QMetaObject::invokeMethod(statusLabel, std::bind(&QLabel::setText, statusLabel, status));
	}
	void Start(std::wstring chromePath, bool headless)
	{
		if (process)
			DevTools::Close();

		auto args = FormatString(
			L"%s --proxy-server=direct:// --disable-extensions --disable-gpu --no-first-run --user-data-dir=\"%s\\devtoolscache\" --remote-debugging-port=9222",
			chromePath,
			std::filesystem::current_path().wstring());
		args += headless ? L" --window-size=1920,1080 --headless" : L" --window-size=850,900";
		DWORD exitCode = 0;
		STARTUPINFOW DUMMY = {sizeof(DUMMY)};
		PROCESS_INFORMATION processInfo = {};
		if (!CreateProcessW(NULL, args.data(), nullptr, nullptr, FALSE, 0, nullptr, nullptr, &DUMMY, &processInfo))
			return StatusChanged("StartupFailed");
		CloseHandle(processInfo.hThread);
		process = processInfo.hProcess;

		if (HttpRequest httpRequest{
				L"Mozilla/5.0 Textractor",
				L"127.0.0.1",
				L"POST",
				L"/json/list",
				"",
				NULL,
				9222,
				NULL,
				WINHTTP_FLAG_ESCAPE_DISABLE})
			if (auto list = Copy(JSON::Parse(httpRequest.response).Array()))
				if (auto it = std::find_if(
						list->begin(),
						list->end(),
						[](const JSON::Value<wchar_t> &object)
						{ return object[L"type"].String() && *object[L"type"].String() == L"page" && object[L"webSocketDebuggerUrl"].String(); });
					it != list->end())
					return webSocket.open(S(*(*it)[L"webSocketDebuggerUrl"].String()));

		StatusChanged("ConnectingFailed");
	}

	auto _ = ([]
			  {
		QObject::connect(&webSocket, &QWebSocket::stateChanged,
			[](QAbstractSocket::SocketState state) { StatusChanged(QMetaEnum::fromType<QAbstractSocket::SocketState>().valueToKey(state)); });
		QObject::connect(&webSocket, &QWebSocket::textMessageReceived, [](QString message)
		{
			auto result = JSON::Parse(S(message));
			auto mapQueue = ::mapQueue.Acquire();
			if (auto id = result[L"id"].Number()) if (auto request = mapQueue->find((int)*id); request != mapQueue->end())
			{
				request->second.set(result);
				mapQueue->erase(request);
			}
		}); }(), 0);
}

namespace DevTools
{
	void Initialize()
	{
		QString chromePath = settings.value(CHROME_LOCATION).toString();
		if (chromePath.isEmpty())
		{
			for (auto [_, process] : GetAllProcesses())
				if (process && (process->find(L"\\chrome.exe") != std::string::npos || process->find(L"\\msedge.exe") != std::string::npos))
					chromePath = S(process.value());
			wchar_t programFiles[MAX_PATH + 100] = {};
			for (auto folder : {CSIDL_PROGRAM_FILESX86, CSIDL_PROGRAM_FILES, CSIDL_LOCAL_APPDATA})
			{
				SHGetFolderPathW(NULL, folder, NULL, SHGFP_TYPE_CURRENT, programFiles);
				wcscat_s(programFiles, L"/Google/Chrome/Application/chrome.exe");
				if (std::filesystem::exists(programFiles))
					chromePath = S(programFiles);
			}
		}
		auto chromePathEdit = new QLineEdit(chromePath);
		static struct : QObject
		{
			bool eventFilter(QObject *object, QEvent *event)
			{
				if (auto mouseEvent = dynamic_cast<QMouseEvent *>(event))
					if (mouseEvent->button() == Qt::LeftButton)
						if (QString chromePath = QFileDialog::getOpenFileName(nullptr, TRANSLATION_PROVIDER, "/", "Google Chrome (*.exe)"); !chromePath.isEmpty())
							((QLineEdit *)object)->setText(chromePath);
				return false;
			}
		} chromeSelector;
		chromePathEdit->installEventFilter(&chromeSelector);
		QObject::connect(chromePathEdit, &QLineEdit::textChanged, [chromePathEdit](QString path)
						 { settings.setValue(CHROME_LOCATION, path); });
		display->addRow(CHROME_LOCATION, chromePathEdit);
		auto headlessCheck = new QCheckBox();
		auto startButton = new QPushButton(START_DEVTOOLS), stopButton = new QPushButton(STOP_DEVTOOLS);
		headlessCheck->setChecked(settings.value(HIDE_CHROME, true).toBool());
		QObject::connect(headlessCheck, &QCheckBox::clicked, [](bool headless)
						 { settings.setValue(HIDE_CHROME, headless); });
		QObject::connect(startButton, &QPushButton::clicked, [chromePathEdit, headlessCheck]
						 { Start(S(chromePathEdit->text()), headlessCheck->isChecked()); });
		QObject::connect(stopButton, &QPushButton::clicked, &Close);
		auto buttons = new QHBoxLayout();
		buttons->addWidget(startButton);
		buttons->addWidget(stopButton);
		display->addRow(HIDE_CHROME, headlessCheck);
		auto autoStartCheck = new QCheckBox();
		autoStartCheck->setChecked(settings.value(AUTO_START, false).toBool());
		QObject::connect(autoStartCheck, &QCheckBox::clicked, [](bool autoStart)
						 { settings.setValue(AUTO_START, autoStart); });
		display->addRow(AUTO_START, autoStartCheck);
		display->addRow(buttons);
		statusLabel = new QLabel("Stopped");
		statusLabel->setFrameStyle(QFrame::Panel | QFrame::Sunken);
		display->addRow(DEVTOOLS_STATUS, statusLabel);
		if (autoStartCheck->isChecked())
			QMetaObject::invokeMethod(startButton, &QPushButton::click, Qt::QueuedConnection);
	}

	void Close()
	{
		webSocket.close();
		for (const auto &[_, task] : mapQueue.Acquire().contents)
			task.set_exception(std::runtime_error("closed"));
		mapQueue->clear();

		if (process)
		{
			TerminateProcess(process, 0);
			WaitForSingleObject(process, 1000);
			for (int retry = 0; ++retry < 20; Sleep(100))
				try
				{
					std::filesystem::remove_all(L"devtoolscache");
					break;
				}
				catch (std::filesystem::filesystem_error)
				{
					continue;
				}
		}
		process = NULL;
		StatusChanged("Stopped");
	}

	bool Connected()
	{
		return webSocket.state() == QAbstractSocket::ConnectedState;
	}

	JSON::Value<wchar_t> SendRequest(const char *method, const std::wstring &params)
	{
		concurrency::task_completion_event<JSON::Value<wchar_t>> response;
		int id = idCounter += 1;
		if (!Connected())
			return {};
		mapQueue->try_emplace(id, response);
		QMetaObject::invokeMethod(&webSocket, std::bind(&QWebSocket::sendTextMessage, &webSocket, S(FormatString(LR"({"id":%d,"method":"%S","params":%s})", id, method, params))));
		try
		{
			if (auto result = create_task(response).get()[L"result"])
				return result;
		}
		catch (...)
		{
		}
		return {};
	}
}
