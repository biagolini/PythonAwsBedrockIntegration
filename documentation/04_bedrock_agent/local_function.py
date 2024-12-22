# Note:
# You might need to install the dependency first:
# pip3 install wikipedia-api

import wikipediaapi

def get_wikipedia_url(celebrity_name, language='en'):
    """
    Returns the Wikipedia page link for a famous person, if it exists.

    :param celebrity_name: Name of the famous person
    :return: URL to the Wikipedia page or a message indicating it was not found
    """
    # Initialize the Wikipedia API with an appropriate user agent
    user_agent = 'YourProjectName (youremail@example.com)'
    wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language=language)  # Set the language to English

    # Search for the page with the given name
    page = wiki.page(celebrity_name)

    if page.exists():
        return page.fullurl  # Return the full URL of the page
    else:
        return f"The Wikipedia page for '{celebrity_name}' was not found."

# Example usage
celebrity_name = "Pelé"
language = 'en'
print(get_wikipedia_url(celebrity_name, language))  # Output: URL to the Wikipedia page of Albert Einstein


