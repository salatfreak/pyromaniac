from .components import load, Component
from .utils import render
from .errors import LoadError, RenderError, ComponentError

# Render main component
try:
    main = Component('/dev/stdin', ['stdin'], load('.'))
    print(render(main()), end='')
except LoadError as e: exit(f"Error loading {e.type} from {e.name}: {e}")
except RenderError as e: exit(f"Error rendering {e.name}: {e}")
except ComponentError as e: exit(f"Error in component {e.name}: {e}")
