#pragma once

#include <QString>
#include <QVector>
#include <QHash>
#include <QFile>
#include <QFileInfo>
#include <QDir>
#include <QSettings>
#include <QMainWindow>
#include <QDialog>
#include <QApplication>
#include <QLayout>
#include <QFormLayout>
#include <QLabel>
#include <QPushButton>
#include <QCheckBox>
#include <QSpinBox>
#include <QListWidget>
#include <QMessageBox>
#include <QInputDialog>

static thread_local bool ok;

constexpr auto CONFIG_FILE = u8"Textractor.ini";
constexpr auto WINDOW = u8"Window";

struct Settings : QSettings { Settings(QObject* parent = nullptr) : QSettings(CONFIG_FILE, QSettings::IniFormat, parent) {} };
struct QTextFile : QFile { QTextFile(QString name, QIODevice::OpenMode mode) : QFile(name) { open(mode | QIODevice::Text); } };
struct Localizer { Localizer() { Localize(); } };
inline std::wstring S(const QString& s) { return { s.toStdWString() }; }
inline QString S(const std::string& s) { return QString::fromStdString(s); }
inline QString S(const std::wstring& s) { return QString::fromStdWString(s); }
// TODO: allow paired surrogates
inline void sanitize(QString& s) { s.chop(std::distance(std::remove_if(s.begin(), s.end(), [](QChar ch) { return ch.isSurrogate(); }), s.end())); }
inline QString sanitize(QString&& s) { sanitize(s); return std::move(s); }
