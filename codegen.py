import wingapi

def active_editor_only(func):
  def available():
    app = wingapi.gApplication
    editor = app.GetActiveEditor()
    return editor is not None
  func.available = available
  return func

@active_editor_only
def generate_attribute_initialisation():
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
  init_def = analysis.GetSymbolInfo(klass, method)
  if not init_def or not init_def[0].isCallable:
    return
  scope_content = analysis.GetScopeContents('{}:'.format(klass))
  existing_attribs = [symbol for symbol, info in scope_content.iteritems()
                      if 'attrib' in info]
  code_lines = ['self.{} = {}'.format(arg, arg) 
                for arg in init_def[0].args[1:] 
                if not arg.startswith('*') and not arg in existing_attribs]
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
