#!/usr/bin/env python
"""
This file computes the raw defect energies (for vacancy and antisite defects)
by parsing the vasprun.xml files in the VASP DFT calculations
for binary intermetallics, where the metadata is in the folder name
"""

__author__ = "Bharat Medasani, Enze Chen"
__data__  = "Apr 28, 2020"

import os
import glob
from argparse import ArgumentParser

from pymatgen.ext.matproj import MPRester
from monty.serialization import dumpfn
from monty.json import MontyEncoder
from pymatgen.io.vasp.outputs import Vasprun


def solute_def_parse_energy(mpid, solute, mapi_key=None):
    if not mpid:
        print ("============\nERROR: Provide an mpid\n============")
        return
    if not solute:
        print ("============\nERROR: Provide solute element\n============")
        return

    if not mapi_key:
        with MPRester() as mp:
            structure = mp.get_structure_by_material_id(mpid)
    else:
        with MPRester(mapi_key) as mp:
            structure = mp.get_structure_by_material_id(mpid)

    energy_dict = {}

    solutes = []
    def_folders = glob.glob(os.path.join(
        mpid, "solute*subspecie-{}".format(solute)))
    def_folders += glob.glob(os.path.join(mpid, "bulk"))
    for defdir in def_folders:
        fldr_name = os.path.split(defdir)[1]
        vr_file = os.path.join(defdir, 'vasprun.xml')
        if not os.path.exists(vr_file):
            print (fldr_name, ": vasprun.xml doesn't exist in the folder. " \
                   "Abandoning parsing of energies for {}".format(mpid))
            break       # Further processing for the mpid is not useful

        try:
            vr = Vasprun(vr_file)
        except:
            print (fldr_name, ":Failure, couldn't parse vaprun.xml file. "
                   "Abandoning parsing of energies for {}.".format(mpid))
            break       # Further processing for the mpid is not useful

        if not vr.converged:
            print (fldr_name, ": Vasp calculation not converged. "
                   "Abandoning parsing of energies for {}".format(mpid))
            break       # Further processing for the mpid is not useful

        fldr_fields = fldr_name.split("_")
        if 'bulk' in fldr_fields:
            bulk_energy = vr.final_energy
            bulk_sites = vr.structures[-1].num_sites
        elif 'solute' in fldr_fields:
            site_index = int(fldr_fields[1])
            site_multiplicity = int(fldr_fields[2].split("-")[1])
            site_specie = fldr_fields[3].split("-")[1]
            substitution_specie = fldr_fields[4].split("-")[1]
            energy = vr.final_energy
            solutes.append({'site_index':site_index,
                'site_specie':site_specie,'energy':energy,
                'substitution_specie':substitution_specie,
                'site_multiplicity':site_multiplicity
                })
    else:
        if not solutes:
            print("Solute folders do not exist.")
            return {}

        print ("Solute {} calculations successful for {}.".format(solute,mpid))
        for solute in solutes:
            solute_flip_energy = solute['energy']-bulk_energy
            solute['energy'] = solute_flip_energy
        solutes.sort(key=lambda entry: entry['site_index'])
        energy_dict[mpid] = {'solutes':solutes}
        return energy_dict

    return {} # Return Null dict due to failure


def vac_antisite_def_parse_energy(mpid, mapi_key=None):
    if not mpid:
        print ("============\nERROR: Provide an mpid\n============")
        return

    if not mapi_key:
        with MPRester() as mp:
            structure = mp.get_structure_by_material_id(mpid)
    else:
        with MPRester(mapi_key) as mp:
            structure = mp.get_structure_by_material_id(mpid)

    energy_dict = {}

    antisites = []
    vacancies = []
    def_folders = glob.glob(os.path.join(mpid, "vacancy*"))
    def_folders += glob.glob(os.path.join(mpid, "antisite*"))
    def_folders += glob.glob(os.path.join(mpid, "bulk"))
    for defdir in def_folders:
        fldr_name = os.path.split(defdir)[1]
        vr_file = os.path.join(defdir, 'vasprun.xml')
        if not os.path.exists(vr_file):
            print (fldr_name, ": vasprun.xml doesn't exist in the folder. " \
                   "Abandoning parsing of energies for {}".format(mpid))
            break       # Further processing for the mpid is not useful

        try:
            vr = Vasprun(vr_file)
        except:
            print (fldr_name, ":Failure, couldn't parse vaprun.xml file. "
                   "Abandoning parsing of energies for {}".format(mpid))
            break

        if not vr.converged:
            print (fldr_name, ": Vasp calculation not converged. "
                   "Abandoning parsing of energies for {}".format(mpid))
            break       # Further processing for the mpid is not useful

        fldr_fields = fldr_name.split("_")
        if 'bulk' in fldr_fields:
            bulk_energy = vr.final_energy
            bulk_sites = vr.structures[-1].num_sites
        elif 'vacancy' in fldr_fields:
            site_index = int(fldr_fields[1])
            site_multiplicity = int(fldr_fields[2].split("-")[1])
            site_specie = fldr_fields[3].split("-")[1]
            energy = vr.final_energy
            vacancies.append({'site_index':site_index,
                'site_specie':site_specie,'energy':energy,
                'site_multiplicity':site_multiplicity
                })
        elif 'antisite' in fldr_fields:
            site_index = int(fldr_fields[1])
            site_multiplicity = int(fldr_fields[2].split("-")[1])
            site_specie = fldr_fields[3].split("-")[1]
            substitution_specie = fldr_fields[4].split("-")[1]
            energy = vr.final_energy
            antisites.append({'site_index':site_index,
                'site_specie':site_specie, 'energy':energy,
                'substitution_specie':substitution_specie,
                'site_multiplicity':site_multiplicity
                })
    else:
        print("All calculations successful for {}".format(mpid))
        e0 = bulk_energy / bulk_sites * structure.num_sites
        for vac in vacancies:
            vac_flip_energy = vac['energy'] - bulk_energy
            vac['energy'] = vac_flip_energy
        vacancies.sort(key=lambda entry:entry['site_index'])
        for antisite in antisites:
            as_flip_energy = antisite['energy'] - bulk_energy
            antisite['energy'] = as_flip_energy
        antisites.sort(key=lambda entry:entry['site_index'])
        energy_dict[mpid] = {'structure':structure,
            'e0':e0, 'vacancies':vacancies, 'antisites':antisites}
        return energy_dict

    return {} # Return Null dict due to failure


def im_vac_antisite_def_energy_parse():
    m_description = 'Command to parse vacancy and antisite defect ' \
                    'energies for intermetallics from the VASP DFT ' \
                    'calculations.'

    parser = ArgumentParser(description=m_description)

    parser.add_argument("--mpid",
            type=str.lower,
            help="Materials Project id of the intermetallic structure.\n" \
                 "For more info on Materials Project, please refer to " \
                 "www.materialsproject.org")

    parser.add_argument("--mapi_key",
            default = None,
            help="Your Materials Project REST API key.\n" \
                 "For more info, please refer to " \
                 "www.materialsproject.org/opne")

    args = parser.parse_args()

    energy_dict = vac_antisite_def_parse_energy(args.mpid, args.mapi_key)
    if energy_dict:
        fl_nm = args.mpid + '_raw_defect_energy.json'
        dumpfn(energy_dict, fl_nm, cls=MontyEncoder, indent=4)


def im_sol_sub_def_energy_parse():
    m_description = 'Command to parse solute substitution defect ' \
                    'energies for intermetallics from the VASP DFT ' \
                    'calculations.'

    parser = ArgumentParser(description=m_description)

    parser.add_argument("--mpid",
            type=str.lower,
            help="Materials Project id of the intermetallic structure.\n" \
                 "For more info on Materials Project, please refer to " \
                 "www.materialsproject.org")

    parser.add_argument("--solute",
            type=str,
            help="Solute Element")

    parser.add_argument("--mapi_key",
            default = None,
            help="Your Materials Project REST API key.\n" \
                 "For more info, please refer to " \
                 "www.materialsproject.org/opne")

    args = parser.parse_args()

    energy_dict = solute_def_parse_energy(args.mpid, args.solute,
            args.mapi_key)
    if energy_dict:
        fl_nm = args.mpid + '_solute-' + args.solute + '_raw_defect_energy.json'
        dumpfn(energy_dict, fl_nm, indent=4, cls=MontyEncoder)


if __name__ == '__main__':
    im_vac_antisite_def_energy_parse()
    # im_sol_sub_def_energy_parse()

