from distutils.log import debug
from testy import app

if __name__ == "__main__":
    app.run(debug=True, host= "0.0.0.0", port=81)
    #flask run --host=0.0.0.0