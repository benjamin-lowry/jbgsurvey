from requests import get
from json import load, loads
from time import sleep
from os import makedirs, utime
from os.path import basename, join, exists
from glob import glob

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

# Country codes to add to language tags without country
LANG_COUNTRIES = {"en": ["en-AU", "en-GB", "en-US"]}

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
        if resp.status_code == 200:
            with open(destfile, "wb") as f:
                f.write(resp.content)
            timestamp = int(filename.replace(".json", "").split("-")[-1])
            utime(destfile, (timestamp, timestamp))
            return parse_survey_dict(resp.json())
        else:
            return []

def get_app_config(server, protocol, game_tag):
    resp = get(protocol + "://" + server + "/api/v2/app-configs/" + game_tag,
               headers={"user-agent":USER_AGENT})
    json = resp.json()
    # Find the highest surveyDataFilename timestamp,
    # to name the app-config file
    timestamp = 0
    for key, value in json["body"]["settings"].items():
        if key.startswith("surveyDataFilename_"):
            newstamp = int(value.replace(".json", "").split("-")[-1])
            if newstamp > timestamp: timestamp = newstamp
    makedirs("app-configs", exist_ok=True)
    dest = join("app-configs", "%s.json" % timestamp)
    with open(dest, "wb") as f:
        f.write(resp.content)
    utime(dest, (timestamp, timestamp))
    return json
if __name__ == "__main__":
    app_config = get_app_config(SERVER, PROTOCOL, GAME_TAG)
    for language_contents_filename in glob("content_ids/*.txt"):
        language = basename(language_contents_filename).replace(".txt", "")
        with open(language_contents_filename, "r") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(0)
            content_id = f.readline().strip()
            while content_id:
                print("\r" + language + " %.2f" % round(f.tell() / size * 100, 2) + "%", end="")
                if not content_id in app_config["body"]["settings"]["onlyForLobbyContentIds"]:
                    for lang_country in (LANG_COUNTRIES[language] if language
                                         in LANG_COUNTRIES else [language]):
                        try:
                            responses = get_responses(content_id.split("_")[0].replace("TR-", ""), language,
                              app_config["body"]["settings"]["surveyDataBaseURL"],
                              app_config["body"]["settings"]["surveyDataFilename_" + lang_country])
                        except Exception as e:
                            print("error on content", content_id, "language", language, e)
                content_id = f.readline().strip()
        print()
    print()
