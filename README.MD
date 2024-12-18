## Set up Environment Variables

Run setup.sh and follow the steps to setup required env variables


Retriever Node

So this node is going to get the state.
It's going to extract the question that the user asked.
And it's going to retrieve the relevant documents for that stat.
So that is going to be using our vector store semantic search capabilities.
And after this node we should update the state documents to hold the relevant documents from our vector
store.

Document Grader Node

So after we've implemented the retrieve node, we're going to implement now the document grader node.
So when we enter this node we have in our state the retrieve documents.
So now we want to iterate over those documents and to determine whether they are indeed relevant to
our question or not.
So for that we're going to be writing a retrieval grader chain, which is going to use structured output
from our LM and turning it into a pedantic object that will have the information, whether this document
is relevant or not.

And if the document is not relevant, we want to filter it out and keep only the documents which are
relevant to the question.

And if not all documents are relevant.
So this means that at least one document is not relevant to our query.
Then we want to mark the web search flag to be true.
So we'll go and later search for this term.

Document Grader Chain

And this chain is going to receive as an input the original question and the retrieve document.
And it's going to determine whether the document is relevant to the questions or not.
And we're going to be running this chain for each documents we retrieve.
And we'll be leveraging structured output for this.