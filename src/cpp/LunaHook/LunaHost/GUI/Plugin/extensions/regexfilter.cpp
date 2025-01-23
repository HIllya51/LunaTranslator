#include "qtcommon.h"
#include "extension.h"
#include "ui_regexfilter.h"
#include "blockmarkup.h"
#include <fstream>

extern const char *REGEX_FILTER;
extern const char *INVALID_REGEX;
extern const char *CURRENT_FILTER;

const char *REGEX_SAVE_FILE = "SavedRegexFilters.txt";

std::optional<std::wregex> regex;
std::wstring replace = L"$1";
concurrency::reader_writer_lock m;
DWORD (*GetSelectedProcessId)
() = []
{ return 0UL; };

class Window : public QDialog, Localizer
{
public:
	Window() : QDialog(nullptr, Qt::WindowMinMaxButtonsHint)
	{
		ui.setupUi(this);

		connect(ui.regexEdit, &QLineEdit::textEdited, this, &Window::SetRegex);
		connect(ui.saveButton, &QPushButton::clicked, this, &Window::Save);

		setWindowTitle(REGEX_FILTER);
		// QMetaObject::invokeMethod(this, &QWidget::show, Qt::QueuedConnection);
	}

	void SetRegex(QString regex)
	{
		ui.regexEdit->setText(regex);
		std::scoped_lock lock(m);
		if (!regex.isEmpty())
			try
			{
				::regex = S(regex);
			}
			catch (std::regex_error)
			{
				return ui.output->setText(INVALID_REGEX);
			}
		else
			::regex = std::nullopt;
		ui.output->setText(QString(CURRENT_FILTER).arg(regex));
	}

private:
	void Save()
	{
		auto formatted = FormatString(
			L"\xfeff|PROCESS|%s|FILTER|%s|END|\r\n",
			getModuleFilename(GetSelectedProcessId()).value_or(FormatString(L"Error getting name of process 0x%X", GetSelectedProcessId())),
			S(ui.regexEdit->text()));
		std::ofstream(REGEX_SAVE_FILE, std::ios::binary | std::ios::app).write((const char *)formatted.c_str(), formatted.size() * sizeof(wchar_t));
	}

	Ui::FilterWindow ui;
} window;

bool ProcessSentence(std::wstring &sentence, SentenceInfo sentenceInfo)
{
	static auto _ = GetSelectedProcessId = (DWORD(*)())sentenceInfo["get selected process id"];
	if (sentenceInfo["text number"] == 0)
		return false;
	if (/*sentenceInfo["current select"] && */ !regex)
		if (auto processName = getModuleFilename(sentenceInfo["process id"]))
		{
			std::ifstream stream(REGEX_SAVE_FILE, std::ios::binary);
			BlockMarkupIterator savedFilters(stream, Array<std::wstring_view>{L"|PROCESS|", L"|FILTER|"});
			std::vector<std::wstring> regexes;
			while (auto read = savedFilters.Next())
				if (read->at(0) == processName)
					regexes.push_back(std::move(read->at(1)));
			if (!regexes.empty())
				QMetaObject::invokeMethod(&window, std::bind(&Window::SetRegex, &window, S(regexes.back())), Qt::BlockingQueuedConnection);
		}
	concurrency::reader_writer_lock::scoped_lock_read readLock(m);
	if (regex)
		sentence = std::regex_replace(sentence, regex.value(), replace);
	return true;
}

extern "C" __declspec(dllexport) void VisSetting(bool vis)
{
	if (vis)
		QMetaObject::invokeMethod(&window, &QWidget::show, Qt::QueuedConnection);
	else
		QMetaObject::invokeMethod(&window, &QWidget::hide, Qt::QueuedConnection);
}
