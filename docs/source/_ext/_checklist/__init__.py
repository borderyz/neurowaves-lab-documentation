# _ext/checklist/__init__.py
from docutils import nodes
from sphinx.util.docutils import SphinxDirective

class checklist_node(nodes.General, nodes.Element):
    pass

class group_node(nodes.General, nodes.Element):
    def __init__(self, text):
        super().__init__()
        self['text'] = text

class checkitem_node(nodes.General, nodes.Element):
    def __init__(self, text, checked, key):
        super().__init__()
        self['checked'] = bool(checked)
        self['key'] = key
        self += nodes.Text(text)

def _leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip(' '))

class ChecklistDirective(SphinxDirective):
    has_content = True

    def run(self):
        # inside ChecklistDirective.run(self):
        env = self.env
        root = checklist_node()
        stack = [(0, root)]  # (indent, container checklist_node)
        last_item = None
        seq = 0

        i = 0
        lines = list(self.content)
        n = len(lines)

        def indent_of(s):
            return len(s) - len(s.lstrip(' '))

        while i < n:
            raw = lines[i]
            i += 1
            if not raw.strip():
                continue

            indent = indent_of(raw)
            line = raw.strip()

            # optional leading dash/star
            if line.startswith(('- ', '* ')):
                line = line[2:].lstrip()

            # climb to proper parent level
            while stack and indent < stack[-1][0]:
                stack.pop()
            if not stack:
                stack = [(0, root)]
            parent = stack[-1][1]

            # going deeper than current level -> nest under last_item
            if indent > stack[-1][0]:
                if last_item is None:
                    last_item = group_node("")
                    parent += last_item
                nested = checklist_node()
                last_item += nested
                stack.append((indent, nested))
                parent = nested

            # task?
            if line.lower().startswith('[ ] ') or line.lower().startswith('[x] '):
                checked = (line[1:2].lower() == 'x')
                text = line[4:]
                key = f"{env.docname}::{seq}::{text[:80]}"
                node = checkitem_node(text, checked, key)
                parent += node
                last_item = node
                seq += 1
                continue

            # plain bullet sublist under the LAST item (no checkbox)
            if line.startswith('- '):
                # collect contiguous plain bullets at the SAME indent
                items = [line[2:].lstrip()]
                bullet_indent = indent
                while i < n:
                    peek = lines[i]
                    if not peek.strip():
                        i += 1
                        continue
                    pi = indent_of(peek);
                    pline = peek.strip()
                    if pi != bullet_indent or not pline.startswith('- '):
                        break
                    items.append(pline[2:].lstrip())
                    i += 1

                # attach them: if we’re not nested yet, create a group holder
                holder = last_item if isinstance(last_item, (checkitem_node, group_node)) else parent
                ul = nodes.bullet_list()
                for it in items:
                    li = nodes.list_item('',
                                         nodes.paragraph(text=it))
                    ul += li

                # if holder is a checkitem/group, add ul under it; else directly under parent
                if holder is last_item:
                    holder += ul
                else:
                    parent += ul
                # keep last_item unchanged
                continue

            # otherwise: treat as a group label
            grp = group_node(line)
            parent += grp
            last_item = grp

        return [root]

# ---------------- HTML writer ----------------
def html_depart_checklist_node(self, node):
    self.body.append('</ul></div>')

def html_visit_checklist_node(self, node):
    self.body.append('<div class="checklist-wrap"><ul class="task-list">')

def html_visit_group_node(self, node):
    label = self.encode(node.get('text', ''))
    # Open an <li> for the group; nested checklist(s) will render inside
    self.body.append(f'<li class="task-group"><span class="group-label">{label}</span>')

def html_depart_group_node(self, node):
    self.body.append('</li>')

def html_visit_checkitem_node(self, node):
    checked_attr = ' checked' if node.get('checked') else ''
    key_attr = f' data-key="{self.encode(node.get("key"))}"'
    self.body.append(f'<li><label><input type="checkbox"{checked_attr}{key_attr}> ')

def html_depart_checkitem_node(self, node):
    self.body.append('</label></li>')

# ---------------- LaTeX writer (PDF) ----------------
def latex_visit_checklist_node(self, node):
    self.body.append(r'\begin{itemize}' + '\n')

def latex_depart_checklist_node(self, node):
    self.body.append(r'\end{itemize}' + '\n')

def latex_visit_group_node(self, node):
    text = node.get('text', '')
    self.body.append(r'\item ' + text + '\n')

def latex_depart_group_node(self, node):
    pass

def latex_visit_checkitem_node(self, node):
    box = r'$\boxtimes$' if node.get('checked') else r'$\Box$'
    self.body.append(r'\item ' + box + ' ')

def latex_depart_checkitem_node(self, node):
    pass

def setup(app):
    app.add_node(
        checklist_node,
        html=(html_visit_checklist_node, html_depart_checklist_node),
        latex=(latex_visit_checklist_node, latex_depart_checklist_node),
    )
    app.add_node(
        group_node,
        html=(html_visit_group_node, html_depart_group_node),
        latex=(latex_visit_group_node, latex_depart_group_node),
    )
    app.add_node(
        checkitem_node,
        html=(html_visit_checkitem_node, html_depart_checkitem_node),
        latex=(latex_visit_checkitem_node, latex_depart_checkitem_node),
    )
    app.add_directive("checklist", ChecklistDirective)

    # Optional styling/persistence files (add them if you have them)
    app.add_css_file("checklist.css")
    app.add_js_file("checklist.js")

    return {"version": "0.2", "parallel_read_safe": True}
