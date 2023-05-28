from __future__ import annotations
from typing import Optional, List
from config.crud import crud
from config.db import NRC
from schemas.schemas import TimeFilter, ProfessorFilter
import itertools


class scheduleController():


    @staticmethod
    def blocks_has_conflict(blocks1: List[Block], blocks2: List[Block]) -> bool:
        return any(
            max(block1.parse_time(block1.time_start),
                block2.parse_time(block2.time_start)) <
            min(block1.parse_time(block1.time_end),
                block2.parse_time(block2.time_end)) and
            block1.day == block2.day
            for block1 in blocks1
            for block2 in blocks2
        )
    @staticmethod
    def nrc_has_conflict(olds_nrcs: List["NRC"], nrc: "NRC") -> bool:
        return any(scheduleController.blocks_has_conflict(old_nrc.blocks, nrc.blocks)
                   for old_nrc in olds_nrcs)

    @staticmethod
    def check_combination(combination: List[NRC]) -> bool:
        return all(not scheduleController.nrc_has_conflict(combination[:i], combination[i])
                   for i in range(1, len(combination)))


    @staticmethod
    def get_unique_combinations(combinations: List[List["NRC"]]) -> List[List["NRC"]]:
        unique_combinations = []

        for combination in combinations:
            classcodes = set(nrc.name for nrc in combination)
            if len(classcodes) == len(combination):
                
                unique_combinations.append(combination)

        return unique_combinations


    @staticmethod
    def create_schedule(classcodes: List["str"],time:List[TimeFilter]=None,professor:ProfessorFilter=None ) -> List[List["NRC"]]:
        final_len = len(classcodes)
        nrc_list = crud.get_allnrc_bycc(classcodes, time, professor)
        combinations = itertools.combinations(nrc_list, final_len)
        combinations = list(combinations)
        
        combinations = [list(tuple) for tuple in combinations]

        combinations = scheduleController.get_unique_combinations(combinations)
        valid_combinations = [combination for combination in combinations
                              if scheduleController.check_combination(combination)]
        return valid_combinations
    



 
