from baseparser import BaseParser
from bs4 import BeautifulSoup, NavigableString, Comment

import operator

class NYTParser(BaseParser):
    SUFFIX = '?pagewanted=all'
    domains = ['www.nytimes.com']

    feeder_pat   = '^https?://www.nytimes.com/202'
    feeder_pages = ['http://www.nytimes.com/',
                    'http://www.nytimes.com/pages/world/',
                    'http://www.nytimes.com/pages/national/',
                    'http://www.nytimes.com/pages/todayspaper/',
                    'http://www.nytimes.com/pages/politics/',
                    'http://www.nytimes.com/pages/nyregion/',
                    'http://www.nytimes.com/pages/business/',
                    'http://www.nytimes.com/pages/technology/',
                    'http://www.nytimes.com/pages/sports/',
                    'http://dealbook.nytimes.com/',
                    'http://www.nytimes.com/pages/science/',
                    'http://www.nytimes.com/pages/health/',
                    'http://www.nytimes.com/pages/arts/',
                    'http://www.nytimes.com/pages/style/',
                    'http://www.nytimes.com/pages/opinion/',
                    'http://www.nytimes.com/pages/automobiles/',
                    'http://www.nytimes.com/pages/books/',
                    'http://www.nytimes.com/crosswords/',
                    'http://www.nytimes.com/pages/dining/',
                    'http://www.nytimes.com/pages/education/',
                    'http://www.nytimes.com/pages/fashion/',
                    'http://www.nytimes.com/pages/garden/',
                    'http://www.nytimes.com/pages/magazine/',
                    'http://www.nytimes.com/pages/business/media/',
                    'http://www.nytimes.com/pages/movies/',
                    'http://www.nytimes.com/pages/arts/music/',
                    'http://www.nytimes.com/pages/obituaries/',
#                    'http://www.nytimes.com/pages/realestate/',
                    'http://www.nytimes.com/pages/t-magazine/',
                    'http://www.nytimes.com/pages/arts/television/',
                    'http://www.nytimes.com/pages/theater/',
                    'http://www.nytimes.com/pages/travel/',
#                    'http://www.nytimes.com/pages/fashion/weddings/',
                    'http://topics.nytimes.com/top/opinion/thepubliceditor/']


    def _parse(self, html):
#        print(html)
        soup = BeautifulSoup(html.decode('utf-8'), "html5lib")
        
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        self.meta = soup.find_all('meta')
        try:
            soup.find('meta', attrs={'name':'hdl'}).get('content')
            soup.find('meta', attrs={'name':'dat'}).get('content')
            soup.find('meta', attrs={'name':'byl'}).get('content')
        except AttributeError:
            self.real_article = False
            # return

        try:
            p_tags = list(soup.find("article", {"id":"story"}).find_all('p'))
        except:
            print(html)
            return 
        div = soup.find('div', attrs={'class': 'story-addendum story-content theme-correction'})
        if div:
            p_tags += [div]
        footer = soup.find('footer', attrs={'class':'story-footer story-content'})
        if footer:
            p_tags += list(footer.find_all(lambda x: x.get('class') != 'story-print-citation' and x.name == 'p'))

        p_contents = reduce(operator.concat, [p.contents + [NavigableString('\n')] for p in p_tags], [])

        body_strings  = []
        for node in p_contents:
            if type(node) is NavigableString:
                body_strings.append(node)
            else:
                if node.name == 'br':
                    body_strings.append(' \n ')
                else:
                    try:
                        body_strings.append(node.get_text())
                    except:
                        body_strings.append(node)

        main_body = ''.join(body_strings)

#        authorids = soup.find('div', attrs={'class':'authorIdentification'})
#        authorid = authorids.getText() if authorids else ''

        top_correction = ' '.join(x.getText() for x in
                                   soup.find_all('nyt_correction_top')) or ' '
        bottom_correction = ' '.join(x.getText() for x in
                                   soup.find_all('nyt_correction_bottom')) or ' '

        self.body = '\n'.join([top_correction,
                               main_body,
#                               authorid,
                               bottom_correction,])
#        print(self.body)
                        
