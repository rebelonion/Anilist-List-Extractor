import requests
import csv
#Description: This script will pull your anime list from Anilist and create a CSV file with the data.

# Anilist API endpoint for retrieving user's list
url = "https://graphql.anilist.co"

# Request the user's Anilist username
username = input("Enter your Anilist username: ")

status = [
    "CURRENT",
    "COMPLETED",
    "PLANNING",
    "PAUSED",
    "DROPPED",
    "REPEATING"
]

def add_double_quote(s):
    result = ''
    try:
        for char in s:
            result += char
            if char == '"':
                result += '"'
    except:
        return "none"
    return result


def pulldata(_username):
    with open('anime_list.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Link", "Romaji", "Format", "Status", "Progress/Episodes", "Genres", "Score"])
    for i in range(0, 5):
        # GraphQL query to retrieve user's list
        query = """
            query($username: String) {
            MediaListCollection(userName: $username, type: ANIME, status: %s) {
                lists {
                entries {
                    media {
                    title {
                        romaji
                        english
                    }
                    format
                    episodes
                    genres
                    siteUrl
                    }
                    status
                    progress
                    score
                }
                }
            }
            }
            """ % (status[i])

        # Variables to pass to the query
        variables = {
            "username": username
        }

        # Make the API request
        response = requests.post(url, json={'query': query, 'variables': variables})

        # Check the status code of the response
        if response.status_code != 200:
            print("Error: API request failed with status code", response.status_code)
            print("Response text:", response.text)
            exit(1)

        try:
            # Extract the list data from the response
            data = response.json().get("data", {}).get("MediaListCollection", {}).get("lists", [{}])[0].get("entries", [])

            #in genres, remove the brackets and replace with commas
            for anime in data:
                anime["media"]["genres"] = str(anime["media"]["genres"]).replace("[", "").replace("]", "").replace("'", "")


            # Write the list data to a CSV file
            with open('anime_list.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                for anime in data:
                    english = add_double_quote(anime["media"]["title"]["english"])
                    if english == "none":
                        english = f'=HYPERLINK("{anime["media"]["siteUrl"]}", "{anime["media"]["title"].get("romaji")}")'
                    else:
                        english = f'=HYPERLINK("{anime["media"]["siteUrl"]}", "{english}")'
                    writer.writerow([
                        english,
                        anime["media"]["title"].get("romaji", ""),
                        anime["media"]["format"],
                        anime["status"],
                        f"{anime['progress']}/{anime['media']['episodes']}",
                        anime["media"]["genres"],
                        anime["score"]
                    ])
        except:
            print("No {} Found".format(status[i]))



pulldata(username)
