##Analysis Files

The files here were designed for scraping books from the Gutenberg online repository. It uses direct calls to the Expert AI API weblinks to disambiguate and analyse these books. This data is then formatted and sent to the firebase for the website to publish it's catalogue of books. Hence, the running of this script is independent of the availability of the main website.

This script can be run seperately to update the website's databse if so wished.

##Configuration

To run this script, make sure to have set input these variables into your system environment.
EAI_USERNAME: "your expert ai account username"
EAI_PASSWORD: "your expert ai account password"

Additionally, you must have your firebase token saved as a file in this folder named:
firebase_token.json