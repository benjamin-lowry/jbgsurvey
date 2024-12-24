1. game opens, initializes config sources
2. each config source's load() is called with earlyLookupFn as a function that
performs a lookup from the config sources that are already loaded
    - serverUrl, protocol, and gameTag from the jbg.config.jet source
    are used to construct a URL like
    [protocol]://[serverUrl]/api/v2/app-configs/[gameTag]
    this is a JSON configuration source that provides additional info
    - example url <https://ecast.jackboxgames.com/api/v2/app-configs/bigsurvey>
3. ListDownloader.ListDownload is used to download the list of survey responses
    - finds the surveyDataBaseURL and surveyDataFilename_[iso language code]
      configuration values from the app-config
    - gets the numeric ID of the survey question from the id field in
      BigSurveyQuestion.jet, this gets stored as unlocalizedId
    - builds a URL like [surveyDataBaseURL]/[unlocalizedId]/[surveyDataFilename]
    - survey data filename appears to be constructed from language code and UNIX
      timestamp of generation
4. parse survey data according to following format:
    - JSON object, root is a dict with one key "l" mapped to an array of answers
    - each answer is a dict with "d" = word, "f" = number of responses, "x" =
      bool whether the answer is explicit, "a" = array of synonyms

"onlyForLobbyContentIds" key in app-config indicates questions that don't have
survey data yet, and thus are used only for asking in the lobby
