__version__ = '0.1'

import json

from os.path import exists
from kivy.app import App
import datetime
import time

from kivy.properties import ListProperty, StringProperty, \
    NumericProperty, BooleanProperty, AliasProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock

from database import Data

class Recipies(Screen):
    data = ListProperty()
    filter = BooleanProperty(False)

    def FilterText(self):
        if self.filter:
            return 'Show all'
        else:
            return 'Pick meal!'

    def _get_data_for_widgets(self):
        return [{
            'prop_index': index,
            'prop_name': recipie['name']}
            for index, recipie in enumerate(self.data)]

    data_for_widgets = AliasProperty(_get_data_for_widgets, bind=['data'])


class RecipieView(Screen):
    prop_id = NumericProperty()
    prop_name = StringProperty()
    prop_description = StringProperty()
    prop_ingredients = ListProperty()
    prop_last_cooked = ObjectProperty()

    def set_time(self):
        self.prop_last_cooked = int(time.mktime(datetime.datetime.now().timetuple()))

    def add_ingredient(self):
        ingredient_list = IngredientListPopup()
        ingredient_list.set_parent(self)
        ingredient_list.load_ingredients()
        ingredient_list.open()

    def append_ingredient(self, ingredient):
        self.prop_ingredients.append({'index': len(self.ingredients_data), 'name': ingredient})

    def del_ingredient(self, index):
        del self.prop_ingredients[index]

    def _ingredients(self):
        return [{
            'prop_recipie': self,
            'prop_index': index,
            'prop_name': ingredient['name']}
            for index, ingredient in enumerate(self.prop_ingredients)]

    ingredients_data = AliasProperty(_ingredients, bind=['prop_ingredients'])

    def timestamp_to_datetime(self, timestamp):
        if timestamp == '0' or timestamp == None:
            return 'Never'
        return datetime.datetime.fromtimestamp(
            int(timestamp)
        ).strftime('%Y-%m-%d %H:%M:%S')


class RecipieListItem(BoxLayout):
    prop_id = NumericProperty()
    prop_name = StringProperty()


class MutableTextInput(FloatLayout):
    text = StringProperty()
    multiline = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(MutableTextInput, self).__init__(**kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        self.w_textinput = self.ids.w_textinput.__self__
        self.w_label = self.ids.w_label.__self__
        self.view()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):  # and touch.is_double_tap
            self.edit()
        return super(MutableTextInput, self).on_touch_down(touch)

    def edit(self):
        self.clear_widgets()
        self.add_widget(self.w_textinput)
        self.w_textinput.focus = True

    def view(self):
        self.clear_widgets()
        if not self.text:
            self.w_label.text = "Double tap/click to edit"
        self.add_widget(self.w_label)

    def check_focus_and_view(self, textinput):
        if not textinput.focus:
            self.text = textinput.text
            self.view()


class IngredientListItem(BoxLayout):
    prop_recipie = None
    prop_index = NumericProperty()
    prop_name = StringProperty()

    def del_ingredient(self):
        self.prop_recipie.del_ingredient(self.prop_index)


class IngredientsTree():

    tv = None

    @classmethod
    def build(cls):

        #if exists(cls.pickle_fn()):
        #   result = pickle.load(open(cls.pickle_fn(), "rb" ) )

        tv = TreeView(hide_root=True)
        tv.size_hint = 1, None
        tv.bind(minimum_height=tv.setter('height'))

        data = Data()

        ingredients = data.get_ingredients()

        node_subgroup = None
        for ingredient in ingredients[::-1]:
            if ingredient['food_subgroup'] == None\
                    and ingredient['food_group'] != None:
                node_group = tv.add_node(TreeViewLabel(text=ingredient['food_group']))
            if ingredient['id'] == None\
                    and ingredient['food_group'] != None\
                    and ingredient['food_subgroup'] != None:
                node_subgroup = tv.add_node(TreeViewLabel(text=ingredient['food_subgroup']), node_group)
            elif node_subgroup != None\
                    and ingredient['id'] != None:
                tv.add_node(IngredientListPopupItem(
                    prop_id=ingredient['id'],
                    name=ingredient['name'],
                    name_scientific=ingredient['name_scientific'],
                    description=ingredient['description']),
                    node_subgroup)


        cls.tv = tv

        #pickle.dump(tv, open(cls.pickle_fn(), "wb"))

    @classmethod
    def get_tree(cls):
        return cls.tv

    @classmethod
    def pickle_fn(self):
        return 'ingredient_tree.pickle'


class IngredientListPopup(Popup):
    data = ListProperty()
    categories = ListProperty()
    parentView = None
    ingredientsPopup:BoxLayout = None
    currentTreeView:TreeView = None

    def set_parent(self, parentView):
        self.parentView = parentView

    def load_ingredients(self):
        self.ingredientsPopup = self.ids['ingredientsPopup']
        self.ingredientsPopup.add_widget(IngredientsTree().tv)
        self.currentTreeView = IngredientsTree().tv

    def close(self):
        if self.currentTreeView._selected_node != None:
            self.parentView.append_ingredient(self.currentTreeView._selected_node.name)
        self.ingredientsPopup.remove_widget(self.currentTreeView)
        self.dismiss()


class IngredientListPopupItem(BoxLayout, TreeViewNode):
    prop_id = NumericProperty()
    name = StringProperty()
    name_scientific = StringProperty()
    description = StringProperty()

    def show_info(self):
        content = IngredientInfo(
            prop_id = self.prop_id,
            name=self.name,
            name_scientific=self.name_scientific,
            description=self.description,
        )
        infoPopup = Popup(content = content, title = self.name)
        infoPopup.open()


class IngredientInfo(BoxLayout):
    prop_id = NumericProperty()
    name = StringProperty()
    name_scientific = StringProperty()
    description = StringProperty()

    def close(self):
        self.dismiss()


class RecipieApp(App):

    def build(self):
        self.kv_file = 'recipie.kv'
        self.filter = False
        self.recipies = Recipies(name='recipies')
        self.current_recipie = None
        self.load_recipies()
        self.transition = SlideTransition(duration=.35)
        root = ScreenManager(transition=self.transition)
        root.add_widget(self.recipies)
        IngredientsTree().build()
        return root

    def load_recipies(self):
        if not exists(self.recipie_fn):
            return
        with open(self.recipie_fn) as fd:
            data = json.load(fd)
        self.recipies.data = data

    def save_recipies(self):
        with open(self.recipie_fn, 'w') as fd:
            json.dump(self.recipies.data, fd)

    def del_recipie(self, rec_index):
        del self.recipies.data[rec_index]
        self.save_recipies()
        self.refresh_recipies()
        self.go_recipies()

    def edit_recipie(self, index):
        self.recipie = self.recipies.data[index]
        name = 'recipie{}'.format(index)

        if self.root.has_screen(name):
            self.root.remove_widget(self.root.get_screen(name))

        view = RecipieView(
            name = name,
            prop_id=index,
            prop_name=self.recipie['name'],
            prop_description=self.recipie['description'],
            prop_ingredients=self.recipie['ingredients'],
            prop_last_cooked=self.recipie['last_cooked']
        )

        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name

    def add_recipie(self):
        self.recipies.data.append({'name': 'New recipie',
                                   'description': 'Description',
                                   'date': '0',
                                   'ingredients': []})
        rec_index = len(self.recipies.data) - 1
        self.edit_recipie(rec_index)

    def set_recipie_description(self, id, description):
        self.recipies.data[id].description = description
        self.save_recipies()
        self.refresh_recipies()

    def set_recipie_title(self, id, name):
        self.recipies.data[id].name = name
        self.save_recipies()
        self.refresh_recipies()

    def refresh_recipies(self):
        data = self.recipies.data
        self.recipies.data = []
        self.recipies.data = data

    def isPrefered(self, item):
        if int(item['date']) == 0:
            return True
        return False

    def PickRecipie(self, element):
        if self.recipies.filter:
            self.recipies.filter = False
            self.load_recipies()
        else:
            self.recipies.filter = True
            prefered = list(filter(self.isPrefered, self.recipies.data))
            self.recipies.data = []
            self.recipies.data = prefered

        element.text = self.recipies.FilterText()

    def go_recipies(self, recipie):
        edited_recipie = self.recipies.data[recipie.prop_id]
        edited_recipie['name'] = recipie.prop_name
        edited_recipie['description'] = recipie.prop_description
        edited_recipie['last_cooked'] = recipie.prop_last_cooked
        edited_recipie['ingredients'] = recipie.prop_ingredients
        self.transition.direction = 'right'
        self.root.current = 'recipies'
        self.save_recipies()
        self.refresh_recipies()

    @property
    def recipie_fn(self):
        # return join(self.user_data_dir, 'recipie.json')
        return 'recipie.json'


if __name__ == '__main__':
    RecipieApp().run()
