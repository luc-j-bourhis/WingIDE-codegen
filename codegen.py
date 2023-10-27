import wingapi

def active_editor_only(func):
  def available():
    app = wingapi.gApplication
    editor = app.GetActiveEditor()
    return editor is not None
  func.available = available
  return func

def __generate_code(func):
  def wrapped():
    app = wingapi.gApplication
    editor = app.GetActiveEditor()
    doc = editor.GetDocument()
    fn = doc.GetFilename()
    analysis = app.GetAnalysis(fn)
    if analysis is None:
      return
    scope = editor.GetSourceScope()
    # we want to be in the method of a class, in which case
    # scope = (filename, lineno, class, method)
    if len(scope) != 4:
      return
    klass, method = scope[-2:]
    method_def = analysis.GetSymbolInfo(klass, method)
    if not method_def or not method_def[0].isCallable:
      return 
    code_lines = func(doc, editor, analysis, klass, method, method_def)
    if not code_lines:
      return
    start, end = editor.GetSelection()
    had_newline = False
    if end > start:
      had_newline = doc.GetCharRange(end-1, end) == "\n"
      doc.DeleteChars(start, end)
    pos = start
    if had_newline:
      doc.InsertChars(pos, "\n")
    lineno = doc.GetLineNumberFromPosition(pos)
    indent = ' '*(pos - doc.GetLineStart(lineno))
    code_lines = [code_lines[0]] + [indent + line for line in code_lines[1:]]
    code = '\n'.join(code_lines)+'\n'
    doc.InsertChars(pos, txt=code)
    pos += len(code)
    editor.SetSelection(pos, pos)
  wrapped.__name__ = func.__name__
  wrapped.__doc__ = func.__doc__
  return wrapped

@active_editor_only
@__generate_code
def generate_attribute_initialisation(doc, editor, analysis, 
                                      klass, method, method_def):
  scope_content = analysis.GetScopeContents('{}:'.format(klass))
  existing_attribs = [symbol for symbol, info in scope_content.items()
                      if 'attrib' in info]
  args = []
  for arg in method_def[0].args[1:]:
    if arg.startswith('*') or arg in existing_attribs:
      continue
    i = arg.find(':')
    if i >=0:
      arg = arg[:i]
    args.append(arg)
  code_lines = ['{}.{} = {}'.format(method_def[0].args[0], arg, arg) 
                for arg in args]
  return code_lines

@active_editor_only
@__generate_code
def generate_super_call(doc, editor, analysis, 
                        klass, method, method_def):
  code_lines = ["super().{}({})"
                .format(method, 
                        ', '.join(method_def[0].args[1:]))]
  return code_lines
