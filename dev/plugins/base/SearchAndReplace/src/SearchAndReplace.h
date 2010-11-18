#ifndef SEARCHANDREPLACE_H
#define SEARCHANDREPLACE_H

#include <pluginsmanager/BasePlugin.h>

class SearchWidget;
class SearchResultsDock;

class SearchAndReplace : public BasePlugin
{
	Q_OBJECT
	Q_INTERFACES( BasePlugin )

public:
	enum ModeFlag
	{
		ModeFlagSearch = 0x1,
		ModeFlagReplace = 0x2,
		ModeFlagDirectory = 0x4,
		ModeFlagProjectFiles = 0x8,
		ModeFlagOpenedFiles = 0x10
	};

	enum Mode
	{
		ModeNo = 0,
		ModeSearch = ModeFlagSearch,
		ModeReplace = ModeFlagReplace,
		ModeSearchDirectory = ModeFlagSearch | ModeFlagDirectory,
		ModeReplaceDirectory = ModeFlagReplace | ModeFlagDirectory,
		ModeSearchProjectFiles = ModeFlagSearch | ModeFlagProjectFiles,
		ModeReplaceProjectFiles = ModeFlagReplace | ModeFlagProjectFiles,
		ModeSearchOpenedFiles = ModeFlagSearch | ModeFlagOpenedFiles,
		ModeReplaceOpenedFiles = ModeFlagReplace | ModeFlagOpenedFiles
	};

	enum Option
	{
		OptionNo = 0x0,
		OptionCaseSensitive = 0x1,
		OptionWholeWord = 0x2,
		OptionWrap = 0x4,
		OptionRegularExpression = 0x8,
	};

	Q_DECLARE_FLAGS( Options, Option );
	
	struct Settings
	{
		Settings()
		{
			replaceSearchText = true;
			onlyWhenNotVisible = false;
			onlyWhenNotRegExp = true;
			onlyWhenNotEmpty = true;
		}
		
		bool replaceSearchText;
		bool onlyWhenNotVisible;
		bool onlyWhenNotRegExp;
		bool onlyWhenNotEmpty;
	};
	
	struct Properties
	{
		Properties()
		{
			mode = SearchAndReplace::ModeNo;
			options = SearchAndReplace::OptionNo;
			project = 0;
		}

		QString searchText;
		QString replaceText;
		QString searchPath;
		SearchAndReplace::Mode mode;
		QStringList mask;
		QString codec;
		SearchAndReplace::Options options;
		QMap<QString, QString> openedFiles; // filename, content
		class XUPProjectItem* project;
		QStringList sourcesFiles;
		Settings settings;
	};
	
	virtual QWidget* settingsWidget();
	
	SearchAndReplace::Settings settings() const;
	void setSettings( const SearchAndReplace::Settings& settings );

protected:
	QPointer<SearchWidget> mWidget;
	QPointer<SearchResultsDock> mDock;

	virtual void fillPluginInfos();

	virtual bool install();
	virtual bool uninstall();

protected slots:
	void searchFile_triggered();
	void replaceFile_triggered();
	void searchDirectory_triggered();
	void replaceDirectory_triggered();
	void searchProjectFiles_triggered();
	void replaceProjectFiles_triggered();
	void searchOpenedFiles_triggered();
	void replaceOpenedFiles_triggered();
};

Q_DECLARE_OPERATORS_FOR_FLAGS( SearchAndReplace::Options )

#endif // SEARCHANDREPLACE_H
