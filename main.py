from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from cloudipsp import Api, Checkout
from sqlalchemy.sql.elements import Null

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	isActive = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return self.title

@app.route('/')
def index():
	items = Item.query.order_by(Item.price).all()
	return render_template('index.html', data=items)


@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/buy/<int:id>')
def item_buy(id):
	item = Item.query.get(id)
	api = Api(merchant_id=1396424,
          secret_key='test')
	checkout = Checkout(api=api)
	data = {
    "currency": "RUB",
    "amount": str(item.price) + "00"
	}
	url = checkout.url(data).get('checkout_url')
	return redirect(url)

@app.route('/create', methods=['POST', 'GET'])
def create():
	if request.method == 'POST':
		title = request.form['title']
		price = request.form['price']

		item = Item(title=title, price=price)

		try:
			db.session.add(item)
			db.session.commit()
			return redirect('/')
		except:
			return "Ошибка"
	else:
		return render_template('create.html')

@app.route('/edit', methods=['GET'])
def edit():
	items = Item.query.all()
	return render_template('edit.html', data=items)

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
	item = Item.query.filter(Item.id == id).one()
	if item.id > 0:
		db.session.delete(item)
		db.session.commit()
	return redirect('/edit')

if __name__ == "__main__":
	app.run(debug=True)