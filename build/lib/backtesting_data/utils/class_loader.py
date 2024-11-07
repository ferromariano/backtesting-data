import importlib
import os

class ClassLoader:
    def __init__(self, directory):
        """
        Inicializa el cargador con el directorio donde están los archivos de clase.

        :param directory: Ruta al directorio que contiene los archivos de clase.
        """
        self.directory = directory

    def load_class(self, class_name):
        """
        Carga una clase desde un archivo en el directorio especificado.

        :param class_name: Nombre de la clase (y del archivo) a cargar.
        :return: La clase cargada.
        :raises FileNotFoundError: Si no se encuentra el archivo.
        :raises AttributeError: Si el archivo no contiene la clase esperada.
        """
        # Construye la ruta al archivo y verifica si existe
        file_path = os.path.join(self.directory, f"{class_name}.py")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No se encontró el archivo {file_path} para la clase {class_name}")

        # Carga el módulo dinámicamente
        module_name = f"{self.directory}.{class_name}".replace("/", ".")
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            raise ImportError(f"No se pudo cargar el módulo {module_name}")

        # Verifica si la clase existe en el módulo y la retorna
        if hasattr(module, class_name):
            return getattr(module, class_name)
        else:
            raise AttributeError(f"La clase {class_name} no se encontró en el módulo {module_name}")


# Ejemplo de uso
if __name__ == "__main__":
    #loader = ClassLoader("./backtesting_data/backtesting_data/exchange")
    loader = ClassLoader("backtesting_data/exchange")
    try:
        MyClass = loader.load_class("binance_futures")
        
        print(MyClass)
        
    except (FileNotFoundError, ImportError, AttributeError) as e:
        print(e)



