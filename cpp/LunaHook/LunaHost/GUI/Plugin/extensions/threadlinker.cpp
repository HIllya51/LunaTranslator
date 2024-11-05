#include "qtcommon.h"
#include "extension.h"
#include "ui_threadlinker.h"
#include <QKeyEvent>

extern const char* THREAD_LINKER;
extern const char* LINK;
extern const char* UNLINK;
extern const char* THREAD_LINK_FROM;
extern const char* THREAD_LINK_TO;
extern const char* HEXADECIMAL;

std::unordered_map<int64_t, std::unordered_set<int64_t>> links;
std::unordered_set<int64_t> universalLinks, empty;
bool separateSentences = false; // allow user to change?
concurrency::reader_writer_lock m;

class Window : public QDialog, Localizer
{
public:
	Window() : QDialog(nullptr, Qt::WindowMinMaxButtonsHint)
	{
		ui.setupUi(this);
		ui.linkButton->setText(LINK);
		ui.unlinkButton->setText(UNLINK);
		connect(ui.linkButton, &QPushButton::clicked, this, &Window::Link);
		connect(ui.unlinkButton, &QPushButton::clicked, this, &Window::Unlink);

		setWindowTitle(THREAD_LINKER);
		//QMetaObject::invokeMethod(this, &QWidget::show, Qt::QueuedConnection);
	}

private:
	void Link()
	{
		bool ok1, ok2, ok3, ok4;
		QString fromInput = QInputDialog::getText(this, THREAD_LINK_FROM, HEXADECIMAL, QLineEdit::Normal, "All", &ok1, Qt::WindowCloseButtonHint);
		int from = fromInput.toInt(&ok2, 16);
		if (ok1 && (fromInput == "All" || ok2))
		{
			int to = QInputDialog::getText(this, THREAD_LINK_TO, HEXADECIMAL, QLineEdit::Normal, "", &ok3, Qt::WindowCloseButtonHint).toInt(&ok4, 16);
			if (ok3 && ok4)
			{
				std::scoped_lock lock(m);
				if ((ok2 ? links[from] : universalLinks).insert(to).second)
					ui.linkList->addItem((ok2 ? QString::number(from, 16) : "All") + "->" + QString::number(to, 16));
			}
		}
	}

	void Unlink()
	{
		if (ui.linkList->currentItem())
		{
			QStringList link = ui.linkList->currentItem()->text().split("->");
			ui.linkList->takeItem(ui.linkList->currentRow());
			std::scoped_lock lock(m);
			(link[0] == "All" ? universalLinks : links[link[0].toInt(nullptr, 16)]).erase(link[1].toInt(nullptr, 16));
		}
	}

	void keyPressEvent(QKeyEvent* event) override
	{
		if (event->key() == Qt::Key_Delete) Unlink();
	}

	Ui::LinkWindow ui;
} window;

bool ProcessSentence(std::wstring& sentence, SentenceInfo sentenceInfo)
{
	concurrency::reader_writer_lock::scoped_lock_read readLock(m);
	auto action = separateSentences ? sentenceInfo["add sentence"] : sentenceInfo["add text"];
	auto it = links.find(sentenceInfo["text number"]);
	for (const auto& linkSet : { it != links.end() ? it->second : empty, sentenceInfo["text number"] > 1 ? universalLinks : empty })
		for (auto link : linkSet)
			((void(*)(int64_t, const wchar_t*))action)(link, sentence.c_str());
	return false;
}




extern "C" __declspec(dllexport) void VisSetting(bool vis)
{
	if(vis)
		QMetaObject::invokeMethod(&window, &QWidget::show, Qt::QueuedConnection);
	else
		QMetaObject::invokeMethod(&window, &QWidget::hide, Qt::QueuedConnection);
}
