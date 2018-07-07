This project aims at creating a local and smart content recommendation system.
The system would work on your laptop, learn your preference from what you've
seen before and choose what best to read next. The name is inspired by the 
operating system in Her (2013) but it will be a loooong way there. For now,
it can serve as a playground for natural language processing and recommender
researchers. 

Two features that would make Samantha fun to use and play with:

1. It's uber-personal: it would digest whatever you saw and stored on your 
laptop (but only if you tell it to) and the result would never go anywhere else
2. It covers everything: it would suggest blog posts, Facebook posts, 
public announcements, scientific articles, i.e. whatever that you are 
interested in, not just news articles.

As I said, Samantha needs to go a long way to get there but it's an interesting
problem to tackle!

The main use case is as follows:

1. User downloads and starts the server (runs on [localhost:5000](localhost:5000))
2. User accesses [localhost:5000/import](localhost:5000/import) 
and imports history from a browser
3. After importing, user is returned to home screen and is served recommendations
4. User can click on a recommendation, add it to a collection, subscribe to 
a keyword or vote a recommendation down
5. Depends on user's reaction, the system will update its model so that it
only serves relevant content

As of July 2018, the implemented features are importing from Firefox, 
scraping and detecting some news sources. 