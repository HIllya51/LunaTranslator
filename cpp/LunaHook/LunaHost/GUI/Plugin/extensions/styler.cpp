#include "qtcommon.h"
#include "extension.h"
#include <QPlainTextEdit>

extern const char* LOAD_SCRIPT;

constexpr auto STYLE_SAVE_FILE = u8"Textractor.qss";

class Window : public QDialog, Localizer
{
public:
	Window() : QDialog(nullptr, Qt::WindowMinMaxButtonsHint)
	{
		connect(&loadButton, &QPushButton::clicked, this, &Window::LoadScript);

		if (scriptEditor.toPlainText().isEmpty())
			scriptEditor.setPlainText("/*\nhttps://www.google.com/search?q=Qt+stylesheet+gallery\nhttps://doc.qt.io/qt-5/stylesheet-syntax.html\n*/");
		layout.addWidget(&scriptEditor);
		layout.addWidget(&loadButton);

		resize(800, 600);
		setWindowTitle("Styler");
		//QMetaObject::invokeMethod(this, &QWidget::show, Qt::QueuedConnection);

		LoadScript();
	}

	~Window()
	{
		qApp->setStyleSheet("");
		Save();
	}

private:
	void LoadScript()
	{
		qApp->setStyleSheet(scriptEditor.toPlainText());
		Save();
	}

	void Save()
	{
		QTextFile(STYLE_SAVE_FILE, QIODevice::WriteOnly | QIODevice::Truncate).write(scriptEditor.toPlainText().toUtf8());
	}

	QHBoxLayout layout{ this };
	QPlainTextEdit scriptEditor{ QTextFile(STYLE_SAVE_FILE, QIODevice::ReadOnly).readAll(), this };
	QPushButton loadButton{ LOAD_SCRIPT, this };
} window;

bool ProcessSentence(std::wstring& sentence, SentenceInfo sentenceInfo)
{
	return false;
}


extern "C" __declspec(dllexport) void VisSetting(bool vis)
{
	if(vis)
		QMetaObject::invokeMethod(&window, &QWidget::show, Qt::QueuedConnection);
	else
		QMetaObject::invokeMethod(&window, &QWidget::hide, Qt::QueuedConnection);
}
