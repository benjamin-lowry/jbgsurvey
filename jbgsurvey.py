from requests import get
from json import load, loads
from time import sleep
from os import makedirs
from os.path import join, exists

# Constants from BigSurvey.swf
USER_AGENT = "Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53"
SERVER = "ecast.jackboxgames.com"
PROTOCOL = "https"
GAME_TAG = "bigsurvey"

# Keys used in the survey data JSON
LIST_KEY = "l"
WORD_KEY = "d"
NUM_KEY = "f"
SYNONYMS_KEY = "a"
EXPLICIT_KEY = "x"

# List of languages for which we need to chop off the country code when looking
# up onlyForLobbyContentIds
LANGUAGE_MAP = {"de-DE": "de", "es-ES": "es", "fr-FR": "fr", "it-IT": "it"}

class BigsurveyResponse():
    def __init__(self, word, num, synonyms, explicit):
        # Response word
        self.word = word

        # Number of times this word was used when responding to the survey
        self.num = num

        # List of synonyms for this word
        self.synonyms = synonyms

        # True or false: whether this word should be filtered in
        # Family Friendly mode
        self.explicit = explicit
    def __repr__(self):
        return self.word
    def from_dict(d):
        return BigsurveyResponse(d[WORD_KEY], d[NUM_KEY], d[SYNONYMS_KEY],
                                 d[EXPLICIT_KEY])

def parse_survey_dict(survey_dict):
    return [BigsurveyResponse.from_dict(d) for d in survey_dict[LIST_KEY]]

def get_responses(question_id, language, base_url, filename):
    destdir = join("output", str(question_id))
    makedirs(destdir, exist_ok=True)
    destfile = join(destdir, filename)
    if exists(destfile):
        with open(destfile, "r") as f:
            return parse_survey_dict(load(f))
    else:
        url = base_url + "/" + str(question_id) + "/" + filename
        resp = get(url, headers={"user-agent":USER_AGENT})
        with open(destfile, "wb") as f:
            f.write(resp.content)
        return parse_survey_dict(resp.json())

def get_app_config(server, protocol, game_tag):
    return get(protocol + "://" + server + "/api/v2/app-configs/" + game_tag,
               headers={"user-agent":USER_AGENT}).json()

if __name__ == "__main__":
    app_config = get_app_config(SERVER, PROTOCOL, GAME_TAG)
    all_languages = []
    for key in app_config["body"]["settings"].keys():
        if key.startswith("surveyDataFilename_"):
            all_languages.append(key.replace("surveyDataFilename_", ""))
    scrape_languages = all_languages
    with open("content_ids.txt", "r") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(0)
        content_id = f.readline().strip()
        while content_id:
            print("\r" + "%.2f" % round(f.tell() / size * 100, 2) + "%", end="")
            for language in scrape_languages:
                if language.startswith("en-"):
                    content_ban_id = content_id
                else:
                    if language.find("-") == -1:
                        content_ban_id = content_id + "_" + language + "-" + language.upper()
                    else:
                        content_ban_id = content_id + "_" + language
                if not content_ban_id in app_config["body"]["settings"]["onlyForLobbyContentIds"]:
                    try:
                        responses = get_responses(content_id, language,
                          app_config["body"]["settings"]["surveyDataBaseURL"],
                          app_config["body"]["settings"]["surveyDataFilename_" + language])
                    except Exception as e:
                        print("error on content", content_id, "language", language, e)
            content_id = f.readline().strip()
    print()
