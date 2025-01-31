import logging

def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get the base module name without the package prefix
    base_name = module_name.split('.')[-1]
    
    # Map module names to components for better organization
    component_mapping = {
        'speech_module': 'speech',
        'chat_history': 'data',
        'tab_manager': 'ui',
        'shortcut_manager': 'ui',
        'worker': 'core',
        'ollama_client': 'ai',
        'model_config': 'config',
        'theme_manager': 'ui',
        'dependency_checker': 'system'
    }
    
    # Get the component prefix
    component = component_mapping.get(base_name, 'modules')
    
    # Create logger with component.module_name format
    return logging.getLogger(f"{component}.{base_name}")