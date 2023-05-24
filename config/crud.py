from __future__ import annotations
import json
import itertools
from config.db import db, Department, Classcodes, Majors, NRC, MajorsClasscodes, Block, Teacher
from schemas.schemas import TimeFilter, ProfessorFilter
from src.Scrapping.scrapping import webScrapper
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import joinedload

DPT_PATH = "departamentos.json"
MAJOR_LIST = {'Administración de Empresas': 'PRE00', 
'Arquitectura': 'PRE01', 
'Ciencia de Datos': 'PRE02', 
'Ciencia Política y Gobierno': 'PRE03',
 'Comunicación Social y Periodismo': 'PRE04', 
 'Contaduría Pública': 'PRE05', 'Derecho': 'PRE06', 
 'Diseño Gráfico': 'PRE07', 
 'Diseño Industrial': 'PRE08', 
 'Economía': 'PRE09', 
 'Enfermería': 'PRE010', 
 'Filosofía y Humanidades': 'PRE011',
'Geología': 'PRE012', 
'Ingeniería Civil': 'PRE013', 
'Ingeniería Eléctrica': 'PRE014', 
'Ingeniería Electrónica': 'PRE015',
 'Ingeniería Industrial': 'PRE016', 
'Ingeniería Mecánica': 'PRE017',
'Ingeniería de Sistemas y Computación': 'PRE018',
'Lenguas Modernas y Cultura': 'PRE019',
 'Licenciatura en Educación Infantil': 'PRE020',
'Matemáticas': 'PRE021', 'Medicina': 'PRE022',
 'Música': 'PRE023', 'Negocios Internacionales': 
'PRE024', 'Odontología': 'PRE025', 'Psicología': 
 'PRE026', 'Relaciones Internacionales': 'PRE027'}
ING_SYS = ["MAT1031","MAT1101","IST010","IST2088","CAS3020","MAT1111","FIS1023","IST2089","CAS3030","MAT1121","FIS1043","IST4021" ,"IST2110","MAT4011","FIS1043","IST4031","MAT4021","EST7042","IST4310","IST4330","IST7072"]





class CRUD():
    # Load-Add
    def __init__(self, db):
        self.db = db

    def load_dpt_data(self, data_route: str):
        with open(data_route, 'r') as file:
            data = json.load(file)
        for element in data:
            classcodes = []
            dpt = Department(name=element['NOMBRE_DEL_DPTO'], dpt_code=element['CODE'])
            for cc_name, code in element['CLASSCODES'].items():
                classcodes.append(Classcodes(name=cc_name, cc_code=code, department=dpt))
            self.db.add(dpt)
            self.db.add_all(classcodes)
        self.db.commit()
        self.db.close()

    # Add methods
    def add_majors(self, majors_list: list[str]):
        for name, code in majors_list.items():
            major = Majors(name=name, major_code=code)
            self.db.add(major)
        self.db.commit()

    def add_classcodes(self, major_code: str, classcode_list: list):
        major = self.db.query(Majors).filter(Majors.major_code == major_code).first()
        if major:
            for code in classcode_list:
                classcode = self.db.query(Classcodes).filter(Classcodes.cc_code == code).first()
                if classcode:
                    classcode.majors.append(major)
                else:
                    print("No existe ese classcode")
            self.db.commit()

    def add_major_to_classcode(self, major_code: str, cc_code: str):
        major = self.db.query(Majors).filter(Majors.major_code == major_code).first()
        classcode = self.db.query(Classcodes).filter(Classcodes.cc_code == cc_code).first()
        if major and classcode:
            major_classcode = MajorsClasscodes(major_id=major.id, classcode_id=classcode.id)
            self.db.add(major_classcode)
            self.db.commit()
        else:
            print("Major o Classcode no encontrados")

    def add_nrc(self, ist_list: list):
        for classcode_code in ist_list:
            classcode_ob = self.db.query(Classcodes).filter(Classcodes.cc_code == classcode_code).first()
            if classcode_ob:
                nrc_list = webScrapper.get_allnrcbycode(classcode_code)
                for nrc in nrc_list:
                    nrc_data = {
                        'name': nrc['name'],
                        'nrc': nrc['nrc'],
                        'quotas': int(nrc['quotas']),
                        'cc_code': classcode_ob.cc_code
                    }

                    # Crear una instancia de NRC
                    new_nrc = NRC(**nrc_data)
                    self.db.add(new_nrc)
                    self.db.commit()  # Guardamos el NRC para obtener su ID

                    # Agregar bloques asociados al NRC
                    for block_data in nrc['blocks']:
                        teacher_name = block_data[3]
                        teacher = self.db.query(Teacher).filter(Teacher.name == teacher_name).first()
                        if not teacher:
                            teacher = Teacher(name=teacher_name)
                            self.db.add(teacher)

                        block = Block(
                            day=block_data[0],
                            time_start=block_data[1].split(' - ')[0],
                            time_end=block_data[1].split(' - ')[1],
                            room=block_data[2],
                            teacher=teacher
                        )
                        self.db.add(block)
                        self.db.commit()  # Guardamos el bloque para obtener su ID

                        # Establecer la relación entre el NRC y el bloque
                        new_nrc.blocks.append(block)
                        self.db.commit()  # Guardamos la relación

                    print("Nuevo NRC agregado")
                else:
                    print("Ningún classcode encontrado")

            self.db.commit()

    #Get Methods

    def get_majors(self):
       return db.query(Majors).all()

    def get_classcode(self, code: str):
        return db.query(Classcodes).filter(Classcodes.cc_code == code).first()


    def get_majors_classcodes(self,major_code:str):
       major =  db.query(Majors).filter(Majors.major_code == major_code).first()
       if major:
          classcodes = [classcode for classcode in major.classcodes]
          return classcodes
       
    def get_classcodes_majors(self,classcode_code:str):
       classcode =  db.query(Classcodes).filter(Classcodes.cc_code == classcode_code).first()
       if classcode:
          classcodes = [major.name for major in classcode.majors]
          return classcodes

    def filter_db(self):
     duplicates_query = db.query(NRC.nrc, func.count(NRC.id)).group_by(NRC.nrc).having(func.count(NRC.id) > 1)
     for nrc_value, count in duplicates_query:
         duplicate_records = db.query(NRC).filter(NRC.nrc == nrc_value).all()
         for duplicate in duplicate_records[1:]:
            db.delete(duplicate)
     db.commit()

    def return_majors(self,classcode:str):
        classcode = db.query(Classcodes).filter(Classcodes.cc_code == classcode).first()
        if classcode:
            return [major.name for major in classcode.majors]
        else:
            return []

    def get_professors_by_classcodes(self, classcodes_list: List[str]) -> List[tuple]:
        professor_dict = {}
        professors = (
            db.query(Teacher.name, Classcodes.cc_code)
            .join(Block, Block.teacher_id == Teacher.id)
            .join(NRC, NRC.id == Block.nrc_id)
            .join(Classcodes, Classcodes.cc_code == NRC.cc_code)
            .filter(Classcodes.cc_code.in_(classcodes_list))
            .distinct()
            .all()
        )

        for professor, classcode in professors:
            if professor in professor_dict:
                professor_dict[professor].append(self.get_classcode(classcode).name)
            else:
                professor_dict[professor] = [self.get_classcode(classcode).name]

        return [(professor, classcodes) for professor, classcodes in professor_dict.items()]


    def get_allnrc_bycc(self, classcodes_list: List[str], time_filters: List[TimeFilter] = [],
                    professor_filter: ProfessorFilter = None) -> List[NRC]:
        query = db.query(NRC).join(Classcodes).filter(Classcodes.cc_code.in_(classcodes_list))

        if len(time_filters)>0:
            for time_filter in time_filters:
                time_slots = time_filter.time_slots
                day = time_filter.day
                for time_slot in time_slots:
                    start_time = time_slot.start_time
                    end_time = time_slot.end_time
                    query = query.filter(NRC.blocks.any(Block.day == day,
                                                        Block.time_start >= start_time,
                                                        Block.time_end <= end_time))

        if professor_filter:
            professors = professor_filter.professors
            block_query = db.query(Block.id).join(Teacher).filter(Teacher.name.notin_(professors)).subquery()
            query = query.filter(NRC.blocks.any(Block.id.in_(block_query)))

        nrcs = query.options(joinedload(NRC.classcode)).all()
        return nrcs


crud = CRUD(db)
