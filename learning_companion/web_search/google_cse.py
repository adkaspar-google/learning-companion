import re

from langchain_google_community import GoogleSearchAPIWrapper
from langchain.document_loaders import PyMuPDFLoader, WebBaseLoader

from learning_companion.config import Config

class WebDocSearchGoogleCSE():
    def __init__(self, question, GOOGLE_API_KEY=None, GOOGLE_CSE_ID=None, k=10):
        config = Config()
        if not GOOGLE_API_KEY:
            GOOGLE_API_KEY = config.GOOGLE_API_KEY
        if not GOOGLE_CSE_ID:
            GOOGLE_CSE_ID = config.GOOGLE_CSE_ID
        self.k = k
        self.question = question
        self.google_search_wrapper = GoogleSearchAPIWrapper(
            google_api_key=GOOGLE_API_KEY,
            google_cse_id=GOOGLE_CSE_ID)


    def get_sources(self, num_results=10):
        # Google returns up to 10 results per page, and up to 100 results in total
        # if we want to have more than 10 results, we need to make multiple calls
        # adjusting the 'start' search parameter to switch to a different result
        # page
        search_results = []
        for search_page in range(1, num_results, 10):
            page_result = self.google_search_wrapper.results(
                query=self.question,
                num_results=min(10, num_results),
                search_params={'start': search_page},
            )
            search_results += page_result

        # Extracting only URLs and titles and storing them in a set to avoid duplicates
        sources = set((result['link'], result['title']) for result in search_results)
        print(f'Search completed, returning a total of {len(sources)} sources.')
        return sources

    # Helper function to load all the Google Search results as documents
    def get_documents(self, verbose=False):
        '''
        Helper function to load both html and pdf files from a list of URLs.

        Keyword arguments:
        sources -- a set of tuples (url, title) of the sources that need to be loaded
        verbose -- prints to screen each url with the loading outcome (default False)
        '''
        sources = self.get_sources(10)  # You'll need to provide num_results or use self.k if appropriate
        loaded_documents = []
        total_loaded = 0
        for i, source in enumerate(sources):
            if source:
                # try-except block to handle when a source url fail to be loaded
                try:
                    url = source[0]
                    # removing unnecessary characters from the title
                    title = f'{" ".join(source[1].split())} - {url}'
                    # Checking with Regular Expressions whether the URL points to a PDF
                    if re.search('.pdf', url):
                        loader = PyMuPDFLoader(url)
                    else:
                        loader = WebBaseLoader(url)
                    # loading the document
                    doc = loader.load()[0]
                    # removing unnecessary spacing characters from the text
                    doc.page_content = ' '.join(doc.page_content.split())
                    # adding the cleaned up document to the list of loaded documents
                    doc.metadata['source'] = url
                    doc.metadata['title'] = title
                    loaded_documents.append(doc)
                    if verbose:
                        print(f'Successfully loaded source #{i+1}: {title}')
                    total_loaded += 1
                except Exception as error:
                    # We arrive here if the url is not reachable or it is not supported
                    if verbose:
                        print(f'Failed to load source #{i+1}: {url} - Error: {str(error)}')
        if verbose:
            print(f'Loaded {total_loaded}/{len(sources)} documents.')
        return loaded_documents
