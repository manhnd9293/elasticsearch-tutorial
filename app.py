import re
from flask import Flask, render_template, request
from search import Search

es = Search()

app = Flask(__name__)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    from_ = request.form.get('from_', type=int, default=0)
    results = es.search(
        query={
            'multi_match': {
                'query': query,
                'fields': ['name', 'summary', 'content'],
            }
        }, size = 5, from_=from_
    )
    
    return render_template(
        'index.html', 
        query=query, 
        results=results['hits']['hits'], 
        from_=0, 
        total=results['hits']['total']['value']
        )


@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['name']
    paragraphs = document['_source']['content'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)

@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')