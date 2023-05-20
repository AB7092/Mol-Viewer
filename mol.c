#include "mol.h"
/*
Name: Adarsh Bhavnagariya 
Program Name: mol.c
Last Edited: 02/22/2023
*/


void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
    strcpy(atom->element,element);      //copying values into the atom
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}
void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
    strcpy(element,atom->element);      //copying values from the atom into the argument variables
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    bond->a1 = *a1;                         //copying values into the bond
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;
    compute_coords(bond);
}
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    *a1 = bond->a1;                     //copying values from the bond into the argument variables
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}
void compute_coords( bond *bond ){
    atom *a1 = &bond->atoms[bond->a1];
    atom *a2 = &bond->atoms[bond->a2];
    bond->x1 = a1->x;
    bond->y1 = a1->y;
    bond->x2 = a2->x;
    bond->y2 = a2->y;
    bond->z = (a1->z + a2->z) / 2;
    bond->len = sqrt(pow(a2->x - a1->x, 2) + pow(a2->y - a1->y, 2) + pow(a2->z - a1->z, 2));  //check if correct formula
    bond->dx = (a2->x - a1->x) / bond->len;
    bond->dy = (a2->y - a1->y) / bond->len;
}
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){
    molecule *molptr = malloc(sizeof(struct molecule)); //allocating memory for molecule
    if (molptr == NULL) {
        return NULL;        //return NULL if malloc fails
    }
    molptr->atom_max = atom_max;        
    molptr->atom_no = 0;
    molptr->atoms = malloc(sizeof(struct atom)*atom_max);
    if (molptr->atoms == NULL) {
        return NULL;        //return NULL if malloc fails
    }
    molptr->atom_ptrs = malloc(sizeof(struct atom*)*atom_max);
    if (molptr->atom_ptrs == NULL) {
        return NULL;        //return NULL if malloc fails
    }
    molptr->bond_max = bond_max;
    molptr->bond_no = 0;
    molptr->bonds = malloc(sizeof(struct bond)*bond_max);
    if (molptr->bonds == NULL) {
        return NULL;        //return NULL if malloc fails
    }
    molptr->bond_ptrs = malloc(sizeof(struct bond*)*bond_max);
    if (molptr->bond_ptrs == NULL) {
        return NULL;        //return NULL if malloc fails
    }
    return(molptr);
}
molecule *molcopy( molecule *src ){
    molecule *newmol = molmalloc(src->atom_max,src->bond_max); //creating new molecule with max values of src molecule
 
    for(int i = 0; i < src->atom_no; i++){
        molappend_atom(newmol,&src->atoms[i]);   //appending all atoms from src to new molecule
        
    }
    for (int i = 0; i < src->bond_no; i++){
        molappend_bond(newmol,&src->bonds[i]);   //appending all bonds from src to new molecule
    }

    return(newmol);
}
void molfree( molecule *ptr ){
    free(ptr->atoms);          //freeing all arrays before freeing molecule
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}
void molappend_atom( molecule *molecule, atom *atom ){
    if (molecule->atom_no==molecule->atom_max){ //if atom_no==atom_max, then no room in array. must realloc 
        if (molecule->atom_max==0){     //if atom_max is 0, then incremement by 1; otherwise double
            molecule->atom_max++;       
        } else{
            molecule->atom_max*=2;
        }
        molecule->atoms = realloc(molecule->atoms,sizeof(struct atom)*molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs,sizeof(struct atom*)*molecule->atom_max);
    }
    molecule->atoms[molecule->atom_no] = *atom;   //append new atom at address atom_no                              
    molecule->atom_no++;
    for(int i=0;i<molecule->atom_no;i++){
        molecule->atom_ptrs[i] = &molecule->atoms[i]; //making atom pointers point to their corresponding atoms
    }
}
void molappend_bond( molecule *molecule, bond *bond ){  //same thing as molappend_atom but with bonds
    if (molecule->bond_no==molecule->bond_max){
        if (molecule->bond_max==0){
            molecule->bond_max++;
        } else{
            molecule->bond_max*=2;
        }
        molecule->bonds = realloc(molecule->bonds,sizeof(struct bond)*molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs,sizeof(struct bond*)*molecule->bond_max);
    }
    molecule->bonds[molecule->bond_no] = *bond;                             
    molecule->bond_no++;
    for(int i=0;i<molecule->bond_no;i++){
        molecule->bond_ptrs[i] = &molecule->bonds[i];
    }
}
// Compar function for qsort to compare atoms by z-value
int atom_cmp(const void *a, const void *b){
    struct atom *atom1, *atom2;
    atom1 = *(struct atom**)a;
    atom2 = *(struct atom**)b;
    return((atom1->z > atom2->z)-(atom2->z > atom1->z)); //returns 1 if atom1->z > atom2->z, 0 if equal, -1 is less 
}
//Compar function for qsort to compare bonds by the average of the z-value of their two atoms
int bond_cmp(const void *a, const void *b){
    struct bond *bond1, *bond2;
    bond1 = *(struct bond**)a;
    bond2 = *(struct bond**)b;
    double z1 = bond1->z;
    double z2 = bond2->z;
    return((z1>z2)-(z2>z1));    //returns 1 if z1 > z2, 0 if equal, -1 is less 
}
void molsort( molecule *molecule ){
    qsort(molecule->atom_ptrs,molecule->atom_no,sizeof(struct atom*),atom_cmp);
    qsort(molecule->bond_ptrs,molecule->bond_no,sizeof(struct bond*),bond_cmp);
}
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rad = deg * (M_PI/180.0); //convert degrees to radians
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);

}
void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rad = deg * (M_PI/180.0); //convert degrees to radians
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}
void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    double rad = deg * (M_PI/180.0); //convert degrees to radians
    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}
void mol_xform( molecule *molecule, xform_matrix matrix ){
    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&molecule->bonds[i]);               //computing cords for each bond
    }
    for (int i = 0; i < molecule->atom_no; i++){
        double x = molecule->atoms[i].x;
        double y = molecule->atoms[i].y;
        double z = molecule->atoms[i].z;
        //matrix multiplication 
        molecule->atoms[i].x = (matrix[0][0]*x) + (matrix[0][1]*y) + (matrix[0][2]*z);
        molecule->atoms[i].y = (matrix[1][0]*x) + (matrix[1][1]*y) + (matrix[1][2]*z);
        molecule->atoms[i].z = (matrix[2][0]*x) + (matrix[2][1]*y) + (matrix[2][2]*z);
    }
    
}
