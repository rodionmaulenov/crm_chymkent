class HtmlElement:
    indent_size = 2

    def __init__(self, name, href: str = '', cls: str = '', style: str = '', text: str = ''):
        self.name = name
        self.href = href
        self.cls = cls
        self.style = style
        self.text = text
        self.children = []
        self.parent = None  # Reference to the parent element

    def __str(self, indent: int = 0) -> str:
        # Generate indentation based on current depth
        i = ' ' * (indent * self.indent_size)

        # Start creating the opening tag
        attributes = []
        if self.style:
            attributes.append(f'style="{self.style}"')
        if self.cls:
            attributes.append(f'class="{self.cls}"')
        if self.href:
            attributes.append(f'href="{self.href}"')

        # Combine attributes into a single string
        attr_str = ' '.join(attributes)
        opening_tag = f'<{self.name} {attr_str}>' if attributes else f'<{self.name}>'
        closing_tag = f'</{self.name}>'

        lines = [f'{i}{opening_tag}']
        if self.text:
            lines.append(' ' * ((indent + 1) * self.indent_size) + self.text)

        for child in self.children:
            lines.append(child.__str(indent + 1))

        lines.append(f'{i}{closing_tag}')
        return '\n'.join(lines)

    def __str__(self):
        return self.__str(0)

    def add_child(self, name: str, href: str = '', cls: str = '', style: str = '', text: str = ''):
        child = HtmlElement(name, href, cls, style, text)
        child.parent = self
        self.children.append(child)
        return child  # Returning the child to allow chaining or direct manipulation


class HtmlBuilder:
    def __init__(self, root_name: str, root_style: str = ''):
        self.root = HtmlElement(root_name, root_style)
        self.current = self.root  # This keeps track of the current element being worked on

    def add_child_fluent(self, name: str, href: str = '', cls: str = '', style: str = '',
                         text: str = '') -> 'HtmlBuilder':
        child_element = self.current.add_child(name, href, cls, style, text)
        self.current = child_element  # Move the current context to the new child
        return self  # Return self for fluent chaining

    def go_back(self) -> 'HtmlBuilder':
        if self.current.parent:
            self.current = self.current.parent  # Move up in the hierarchy
        return self

    def __str__(self):
        return str(self.root)
