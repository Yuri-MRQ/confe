import dataset
import psycopg2
from sqlalchemy import create_engine, types
from dataset import Table

# Controle DB
engine = create_engine('postgresql://gnhoadmin:marinhagnho@localhost/controle')

db = dataset.connect('postgresql://gnhoadmin:marinhagnho@localhost/controle')

fornecedores = db['fornecedores']
nota_fiscal = db['nota_fiscal']
empenhos = db['nota_empenho']

#Usuarios DB
engine2 = create_engine('postgresql://gnhoadmin:marinhagnho@localhost/usuarios')

db_usuarios = dataset.connect('postgresql://gnhoadmin:marinhagnho@localhost/usuarios')
usuarios = db_usuarios['usuarios']