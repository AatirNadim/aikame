class DocumentProcessingError(Exception):
  """Raised when there's an error processing a document."""
  pass


class QueryProcessingError(Exception):
  """Raised when there's an error processing a query."""
  pass


class RelativePathError(Exception):
	"""Raised when there's an error with a relative path."""
	pass
