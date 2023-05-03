# Name: Adarsh Bhavnagariya (student ID: 1096488)
# UniversityofGuelph Email: abhavnag@uoguelph.ca
# Program Name: molsql.py
# Last Edited: 04/06/2023

import os;
import sqlite3;
import MolDisplay;
import molecule;

class Database:
    def __init__(self, reset=False):
        if reset and os.path.exists('molecules.db'):
            # delete existing database file if it exists
            os.remove('molecules.db')  
                
        # create database file if it doesn't exist and connect to it
        self.conn = sqlite3.connect('molecules.db')    

    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements
                             ( ELEMENT_NO     INTEGER NOT NULL,
                               ELEMENT_CODE   VARCHAR(3) PRIMARY KEY NOT NULL,
                               ELEMENT_NAME   VARCHAR(32) NOT NULL,
                               COLOUR1        CHAR(6) NOT NULL,
                               COLOUR2        CHAR(6) NOT NULL,
                               COLOUR3        CHAR(6) NOT NULL,
                               RADIUS         DECIMAL(3) NOT NULL );""")
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
                             ( ATOM_ID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                               ELEMENT_CODE   VARCHAR(3) NOT NULL,
                               X              DECIMAL(7,4) NOT NULL,
                               Y              DECIMAL(7,4) NOT NULL,
                               Z              DECIMAL(7,4) NOT NULL,
                               FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE) );""")
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
                             ( BOND_ID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                               A1             INTEGER NOT NULL,
                               A2             INTEGER NOT NULL,
                               EPAIRS         INTEGER NOT NULL );""")
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
                             ( MOLECULE_ID    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                               NAME           TEXT UNIQUE NOT NULL );""")
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                             ( MOLECULE_ID    INTEGER NOT NULL,
                               ATOM_ID        INTEGER NOT NULL, 
                               PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                               FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID)
                               FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID) );""")
        
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                             ( MOLECULE_ID    INTEGER NOT NULL,
                               BOND_ID        INTEGER NOT NULL, 
                               PRIMARY KEY (MOLECULE_ID, BOND_ID),
                               FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID)
                               FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID) );""")
        
        self.conn.commit()

    
    def __setitem__(self, table, values):
        placeholders = ','.join(['?'] * len(values))
        columns = ','.join([col[0] for col in self.conn.execute(f'SELECT * FROM {table}').description]) # Extract column names
        query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        self.conn.execute(query, values)
        self.conn.commit()


    def add_atom(self, molname, atom):
        element_code = atom.atom.element
        x, y, z = atom.atom.x, atom.atom.y, atom.atom.z
        self.conn.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)", (element_code, x, y, z))
        atom_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        mol_id = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,)).fetchone()[0]
        self.conn.execute("INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)", (mol_id, atom_id))
        self.conn.commit()

    def add_bond(self, molname, bond):
        a1, a2, epairs = bond.bond.a1, bond.bond.a2, bond.bond.epairs
        self.conn.execute("INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", (a1, a2, epairs))
        bond_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        mol_id = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,)).fetchone()[0]
        self.conn.execute("INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)", (mol_id, bond_id))
        self.conn.commit()

    def add_molecule(self, name, fp):
        mol = MolDisplay.Molecule()
        mol.parse(fp)
        self.conn.execute("INSERT INTO Molecules (NAME) VALUES (?)", (name,))
        self.conn.commit()

        for i in range(mol.atom_no):
            atom = MolDisplay.Atom(mol.get_atom(i))
            self.add_atom(name, atom)

        for i in range(mol.bond_no):
            bond = MolDisplay.Bond(mol.get_bond(i))
            self.add_bond(name, bond)

    #loading molecule from the database by its name and return a MolDisplay.Molecule object
    def load_mol(self, name):
        mol = MolDisplay.Molecule()
        
        atom_query = """SELECT Atoms.*
                        FROM Atoms
                        JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
                        JOIN Molecules ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                        WHERE Molecules.NAME = ?
                        ORDER BY Atoms.ATOM_ID"""
        
        for atom in self.conn.execute(atom_query, (name,)):
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])
        
        bond_query = """SELECT Bonds.*
                        FROM Bonds
                        JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
                        JOIN Molecules ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                        WHERE Molecules.NAME = ?
                        ORDER BY Bonds.BOND_ID"""
        
        for bond in self.conn.execute(bond_query, (name,)):
            mol.append_bond(bond[1], bond[2], bond[3])
        
        return mol


    def radius(self):
        radii = {}
        for element_code, radius in self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements;"):
            radii[element_code] = radius
        return radii

    def element_name(self):
        element_names = {}
        for element_code, element_name in self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements;"):
            element_names[element_code] = element_name
        return element_names

    def radial_gradients(self):
        radialGradientSVG = """
          <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
            <stop offset="0%%" stop-color="#%s"/>
            <stop offset="50%%" stop-color="#%s"/>
            <stop offset="100%%" stop-color="#%s"/>
          </radialGradient>"""
        
        gradients = []
        for element_name, colour1, colour2, colour3 in self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements;"):
            gradients.append(radialGradientSVG % (element_name, colour1, colour2, colour3))
        
        return ''.join(gradients)
    
    def get_molecule_names(self):
        return [row[0] for row in self.conn.execute("SELECT NAME FROM Molecules;")]




# if __name__ == "__main__":
#   db = Database(reset=True);
#   db.create_tables();
#   db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
#   db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
#   db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
#   db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );

#   fp = open( 'water-3D-structure-CT1000292221.sdf' );
#   db.add_molecule( 'Water', fp );
#   fp = open( 'caffeine-3D-structure-CT1001987571.sdf' );
#   db.add_molecule( 'Caffeine', fp );
#   fp = open( 'CID_31260.sdf' );
#   db.add_molecule( 'Isopentanol', fp );

#   print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
#   print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() );
#   print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() );
#   print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() );
#   print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() );
#   print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() );


# if __name__ == "__main__":
#   db = Database(reset=False); # or use default
#   MolDisplay.radius = db.radius();
#   MolDisplay.element_name = db.element_name();
#   MolDisplay.header += db.radial_gradients();
#   for molecule in [ 'Water']:
#     mol = db.load_mol( molecule );
#     mol.sort();
#     fp = open( molecule + ".svg", "w" );
#     fp.write( mol.svg() );
#     fp.close();