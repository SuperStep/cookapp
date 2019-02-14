'''
        tv = TreeView(hide_root=True)
        tv.size_hint = 1, None
        tv.bind(minimum_height=tv.setter('height'))

        data = Data()
        groups = data.get_groups()
        ingredients = data.get_ingredients()

        def already_created(node, text):
            if hasattr(node, 'text'):
                return node.text == text
            else:
                return False

        for group in groups:
            if len(list(filter(lambda seq: already_created(seq, group['group']), tv.iterate_all_nodes()))) == 0:
                node_group = tv.add_node(TreeViewLabel(text=group['group']))

            node_group = list(filter(lambda seq: already_created(seq, group['group']), tv.iterate_all_nodes()))
            if len(node_group) > 0:
                if len(list(filter(lambda seq: already_created(seq, group['subgroup']), tv.iterate_all_nodes()))) == 0:
                    node_subgroup = tv.add_node(TreeViewLabel(text=group['subgroup']), node_group[0])

        for ingredient in ingredients:
            node_subgroup = list(
                filter(lambda seq: already_created(seq, ingredient['food_subgroup']), tv.iterate_all_nodes()))
            if len(node_subgroup) > 0:
                tv.add_node(IngredientListPopupItem(
                    prop_id=ingredient['id'],
                    name=ingredient['name'],
                    name_scientific=ingredient['name_scientific'],
                    description=ingredient['description']),
                    node_subgroup[0])
            else:
                print('error adding {0}', ingredient['name'])

        cls.tv = tv
'''