
# Name: Adarsh Bhavnagariya 
# Program Name: MolDisplay.py
# Last Edited: 04/05/2023


import molecule;

radius = { 'H': 25, 'C': 40, 'O': 40, 'N': 40,}

element_name = { 'H': 'grey', 'C': 'black', 'O': 'red', 'N': 'blue',}

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500

class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return f"Atom {self.atom.element}: ({self.atom.x}, {self.atom.y}, {self.atom.z})"

    def svg(self):
        x = self.atom.x * 100.0 + offsetx
        y = self.atom.y * 100.0 + offsety
        r = radius[self.atom.element]
        fill = element_name[self.atom.element]
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n'%(x,y,r,fill)

# SVG:
# -cx = center of circles x coordinate
# -cy = center of circles y coordinate
# -r = radius
# -fill is colour
# Thick line is a thick rectangle (polygon)
# -each polygon has 4 corners, all in one string, each corner has x and y

class Bond:
    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self):
        return f"Bond {self.bond.a1} {self.bond.a2} {self.bond.epairs} {self.bond.x1} {self.bond.y1} {self.bond.x2} {self.bond.y2} {self.bond.len} {self.bond.dx} {self.bond.dy}"

    def svg(self):
        x1 = self.bond.x1 * 100.0 + offsetx
        y1 = self.bond.y1 * 100.0 + offsety
        x2 = self.bond.x2 * 100.0 + offsetx
        y2 = self.bond.y2 * 100.0 + offsety
        perpX = self.bond.dx*10.0                 #move perpendicularly to the direction of the bond 10 pixels from the centre
        perpY = self.bond.dy*10.0
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n'%(x1-perpY,y1-perpX,x1+perpY,y1+perpX,x2+perpY,y2+perpX,x2-perpY,y2-perpX)


class Molecule(molecule.molecule):

    def parse(self, file_obj):
            atomNum = 0
            bondNum = 0
            for lineNum, line in enumerate(file_obj, 1):
                if lineNum == 4:                                #gets number of atoms and number of bonds from 4th line
                    lineData = line.split()
                    atomNum = int(lineData[0]) + lineNum
                    bondNum = int(lineData[1]) + int(lineData[0]) + lineNum
                    # print(f"atomnum: {atomNum} bondnum: {bondNum}")
                    continue

                if lineNum>4 and lineNum <=atomNum:        #parse atoms and append them
                    atomData = line.split()
                    element = atomData[3]
                    x, y, z = map(float, atomData[:3])
                    # print (f"ATOM: {x} {y} {z}")
                    self.append_atom(element, x, y, z)
                if lineNum>atomNum and lineNum<=bondNum:  #parse bonds and append them
                    bondData = line.split()
                    # print (f"BOND: {bondData[0:3]}")
                    a1,a2,epairs = map(int, bondData[:3])
                    self.append_bond(a1-1,a2-1,epairs)
                if line.split()=="M  END":
                    break

    def __str__(self):  #prints atoms and bonds for debugging purposes
        string = ""
        for i in range(self.atom_no):
            string+= str(Atom(self.get_atom(i)))
            string+="\n"
        for i in range(self.bond_no):
            string+= str(Bond(self.get_bond(i)))
            string+="\n"
        return string
    def svg(self):
        string = header +"\n"

        a1 = 0
        b1 = 0
        while a1<self.atom_no and b1<self.bond_no:   #applies final pass of a merge sort function to interleave the two arrays of atoms and bonds by z value
            if self.get_atom(a1).z < self.get_bond(b1).z:
                string+= Atom(self.get_atom(a1)).svg()
                a1+=1
            else:
                string+= Bond(self.get_bond(b1)).svg()
                b1+=1

        while a1<self.atom_no: #appending any remaining values from atoms
            string+= Atom(self.get_atom(a1)).svg()
            a1+=1
        while b1<self.bond_no: #appending any remaining values from bonds
            string+= Bond(self.get_bond(b1)).svg()
            b1+=1
        string+= footer
        return string
    def sortMol(self):
        self.sort()



# filename = input("Enter a filename: ")

# with open(filename) as file_obj:
#     mol = Molecule()
#     mol.parse(file_obj)

# mol.sort()

# with open("output.svg", "w") as f:
#     f.write(mol.svg())
