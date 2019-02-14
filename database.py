from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy import create_engine, text
from references import Ingredient, Recipie, RecipieIngredients


class Connection():
    Session = sessionmaker()
    engine = create_engine('mysql+pymysql://root:20122006@localhost/Application', echo=True)
    #engine = create_engine('sqlite:///mydb.db', echo=True)
    Session.configure(bind=engine)
    session = Session()

    def get_recipies(self):
        query = self.session.query(Recipie).order_by(Recipie.id)
        #query = self.session.query(Ingredient).order_by(Ingredient.id)
        return query.all()

    def get_ingredients(self):
        sql = text('''
        SELECT 
            food_group as food_group,
            food_subgroup as food_subgroup,
            id as id,
            max(name) as name,
            max(name_scientific) as name_scientific,
            max(description) as description,
            max(food_type) as food_type,
            max(category) as category,
            max(ncbi_taxonomy_id) as ncbi_taxonomy_i
        FROM Application.Ingredients
        group by 
        food_group desc, 
        food_subgroup desc,
        id desc
        with rollup
        ''')
        result = self.engine.execute(sql)
        for row in result:
            yield row

    '''
    def get_ingredients(self):
        query:Query= self.session.query(Ingredient).order_by(Ingredient.id)
        return query.all()
    '''
    def add(self, object):
        print(self.session)
        self.session.add(object)



class Data():

    def get_ingredients(self):
        conn = Connection()
        ingredient_list = conn.get_ingredients()

        ingredients = []

        for ing in ingredient_list:
            ingredients.append({'id': ing.id,
                                'name': '' if ing.name == None else ing.name,
                                'name_scientific': '' if ing.name_scientific == None else ing.name_scientific,
                                'food_group': ing.food_group,
                                'food_subgroup': ing.food_subgroup,
                                'description': '' if ing.description == None else ing.description})

        return ingredients