"""Patches for Streamlit to fix known issues."""

import sys
import types


def apply_torch_classes_patch():
    """
    Apply a patch to prevent Streamlit file watcher from raising errors with torch.classes.

    This works by creating a fake torch.classes module with a proper __path__ attribute.
    """
    try:
        import torch

        if hasattr(torch, "classes"):
            # Create a new module object to replace torch.classes
            mock_classes = types.ModuleType("torch.classes")

            # Add a proper __path__ attribute that won't cause errors
            mock_classes.__path__ = ["torch_classes_path"]

            # Replace the real torch.classes with our mock
            sys.modules["torch.classes"] = mock_classes
            torch.classes = mock_classes

            print("Applied torch.classes patch for Streamlit file watcher")

    except ImportError:
        # If torch isn't installed, do nothing
        pass
    except Exception as e:
        print(f"Failed to apply torch.classes patch: {str(e)}")
