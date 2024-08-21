# Mercari Notifier

Runs a job that looks for a specified keyword in Mercari Search results, then notifies the user via email if a hit was found and a link to that search result.

## Settings

The following environment variables must be set:

| ENV VAR                      | Description                                                                                                                                                              |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FROM_EMAIL                   | The email you want the notification to be sent from.                                                                                                                     |
| TO_EMAIL                     | The email you want the notification to be sent to.                                                                                                                       |
| GM                           | The [Gmail App Password](https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237) for the Gmail Account you want to send the notification from.                                                                                     |
| MERCARI_KEYWORD_QUERY_STRING | The query string after the "keyword" portion of a Mercari Search url, e.g. "headphones&order=desc&sort=created_time"                                                     |
| SUB_KEYWORD_SEARCH           | A string representing a fine-grained needle-in-the-haystack to further refine the search results resulting from the MERCARI_KEYWORD_QUERY_STRING, e.g. "mint condition"  |

## Running

You will need to either run this manually or set it up to run in [Github Actions](https://docs.github.com/en/actions). A sample Github Action script written in YAML is provided in this repository.
