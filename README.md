# jbgsurvey

This is a simple tool to download the survey data (list of user-generated
responses for each question) used by [*The Jackbox Survey Scramble*][jbgs].
Technically you could use this to cheat but I mainly wrote it because not all of
the modes in the game reveal the answers you failed to guess at the end of the
game and I wanted to find out what they were (plus you can archive the old
versions of the survey data to see how responses change over time).

[jbgs]: https://www.jackboxgames.com/games/the-jackbox-survey-scramble

## Usage

Requires requests installed (``pip3 install -r requirements.txt``). Run
``python3 jbgsurvey.py`` to scrape all the survey responses (for all 9 supported
language variants), which will be stored as JSON files in subfolders of the
output folder. Each folder will be named after the "content ID" of the survey
question; you can find this by looking at
games/BigSurvey/content/[language]/BigSurveyQuestion.jet in the game folder.

(The list of questions to scrape answers for is stored in the text files in the
content_ids folder; these files were generated using list_content_ids.py. If you
need to regenerate these lists, e.g. if they updated the game to add new
questions, you can run ``python3 list_content_ids.py
path/to/games/content/manifest.jet``.)

## TODO

I'd like to add some kind of fancy output; maybe convert the most popular
answers to a CSV or webpage or something.

## License

Copyright 2024 Benjamin Lowry

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
