This project grows from my frustration searching for an news app that is truly
private. You're always asked to store your data remotely somewhere, being able
to choose between servers (as is the case of Disapora) doesn't make it much
different.

What I would like to have is a software that runs on my laptop and never send
my personal data anywhere (except maybe with my friends). 
At the same time, it needs to offer wide enough 
coverage of the news I like including posts by my friends and family members.
Plus, it should be smart about recommending the right articles so that it 
won't overload me.

The main use case is as follows:

1. User downloads and starts eigennews server (runs on [localhost:5000](localhost:5000))
2. User accesses [localhost:5000/import](localhost:5000/import) 
and imports history from a browser
3. After importing, user is returned to home screen and is served recommendations
4. User can click on a recommendation, add it to a collection, subscribe to 
a keyword or vote a recommendation down
5. Depends on user's reaction, the system will update its model so that it
only serves relevant content

As of June 2018, only importing from Firefox and scraping from some news sources
is implemented. 