from os.path import exists
import os
from google.cloud import translate

from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy import create_engine, text
from references import Ingredient, Recipie, RecipieIngredients
import pickle

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/egor_darya/googletrans.json"

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

    cache = {}

    def ingredients_fn(self):
        return 'ingredients.pickle'

    def get_ingredients(self, translate = False):

        if exists(self.ingredients_fn()):
           return pickle.load(open(self.ingredients_fn(), "rb" ))

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

        if translate:
            ingredients = list(map(lambda x: self.Translate(x), ingredients))

        pickle.dump(ingredients, open(self.ingredients_fn(), "wb"))
        return ingredients

    def Translate(self, ingredient, lang = 'ru'):
        translate_client = translate.Client()
        translates = ['name','food_group','food_subgroup']
        for property in translates:
            if ingredient[property] == '':
                continue
            suggesstion = self.cache.get(ingredient[property])
            if suggesstion == None:
                try:
                    translation = translate_client.translate(ingredient[property],
                                                             target_language=lang,
                                                             source_language='en')
                    ingredient[property] = translation['translatedText']
                except Exception:
                    print('error translate {0}', ingredient[property])
            else:
                ingredient[property] = suggesstion


        print(ingredient)
        return ingredient
