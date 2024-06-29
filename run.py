import os
import uvicorn

if __name__ == "__main__":
    # Получаем путь к директории, где находится run.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Путь к директории app
    app_dir = current_dir

    # Меняем текущую рабочую директорию на app
    os.chdir(app_dir)

    # Запускаем Uvicorn с указанием пути к FastAPI приложению
    uvicorn.run("main:app", host="0.0.0.0", port=8000)