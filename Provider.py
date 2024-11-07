


class Data_provider:
    def __init__(self,syouhin_code, syouhin_name,line,line_name,iri_me,ryousoku,tenpahin,yousoka,KI,syoukai_gentei,saishu_gentai,
                  stretch,yotei_syourou,nouki,ticket_no,bikou,MOS,Allergy,seisanbi,jyounban,slot,SV_time_taken,SP_time_taken,nouki_copy,firsts,no_renzoku_seisan,
                  clean_time,kouyousoka_maya,lasts,last_first,weight_limit,only_two,mc_renzo,stretch_flag,nitrogen_gas,SP_per_hour,SV_per_hour,packaging,used,cleaning_jikan):
        
        self.__syouhin_code=syouhin_code
        self.__syouhin_name=syouhin_name
        self.__line=line
        self.__line_name=line_name
        self.__iri_me=iri_me
        self.__ryousoku=ryousoku
        self.__tenpahin=tenpahin
        self.__yousoka=yousoka
        self.__KI=KI
        self.__syoukai_gentei=syoukai_gentei
        self.__saishu_gentai=saishu_gentai
        self.__stretch=stretch
        self.__yotei_syourou=yotei_syourou
        self.__nouki=nouki
        self.__ticket_no=ticket_no
        self.__bikou=bikou
        self.__MOS=MOS
        self.__Allergy=Allergy
        self.__seisanbi=seisanbi
        self.__jyounban=jyounban
        self.__slot=slot
        # self.__time_taken=time_taken
        self.__SV_time_taken=SV_time_taken
        self.__SP_time_taken=SP_time_taken
        self.__nouki_copy=nouki_copy
        self.__firsts=firsts
        self.__no_renzoku_seisan=no_renzoku_seisan
        self.__clean_time=clean_time
        self.__kouyousoka_maya=kouyousoka_maya
        self.__lasts=lasts
        self.__last_first=last_first
        self.__weight_limit=weight_limit
        self.__only_two=only_two
        
        self.__used=used
        self.__cleaning_jikan=cleaning_jikan
        self.__clean1=0
        self.__mc_renzo=mc_renzo

        self.__end_time=nouki_copy
        self.__st_time=None
        self.__stretch_flag=stretch_flag
        
        self.__priority=1
        self.__nitrogen_gas=nitrogen_gas
        self.__SP_per_hour=SP_per_hour
        self.__SV_per_hour=SV_per_hour
        self.__Line_name= None

        self.__start_date_time=None
        self.__end_date_time=None

        self.__packaging=packaging

        self.record_break=0
        # self.__clean_time=clean_time
        # self.__next_renzoku=next_renzoku

    def get_packaging(self):
        return self.__packaging

    def get_start_date_time(self):
        return self.__start_date_time
    
    def get_end_date_time(self):
        return self.__end_date_time
    
    def set_start_datetime(self,date):
        self.__start_date_time=date

    def set_end_datetime(self,date):
        self.__end_date_time=date

    def get_line_name(self):
        return self.__Line_name
    
    def set_line_name(self,line):
        self.__Line_name=line
    
    def get_sp_rate(self):
        return self.__SP_per_hour
    
    def get_sv_rate(self):
        return self.__SV_per_hour

    def get_syouhin_code(self):
        return self.__syouhin_code

    def get_syouhin_name(self):
        return self.__syouhin_name
    
    def get_line(self):
        return self.__line
    
    def get_line_name(self):
        return self.__line_name

    def get_iri_me(self):
        return self.__iri_me

    def get_ryousoku(self):
        return self.__ryousoku
    
    def get_tenpahin(self):
        return self.__tenpahin

    def get_yousoka(self):
        return self.__yousoka

    def get_KI(self):
        return self.__KI
    
    def get_syoukai_gentei(self):
        return self.__syoukai_gentei
    
    def get_saishu_gentei(self):
        return self.__saishu_gentai

    def get_stretch(self):
        return self.__stretch

    def get_yotei_syourou(self):
        return self.__yotei_syourou

    def get_nouki(self):
        return self.__nouki

    def get_ticket_no(self):
        return self.__ticket_no
    
    def get_bikou(self):
        return self.__bikou
    
    def get_MOS(self):
        return self.__MOS
    
    def get_Allergy(self):
        return self.__Allergy

    def get_seisanbi(self):
        return self.__seisanbi

    def get_jyounban(self):
        return self.__jyounban

    def get_slot(self):
        return self.__slot

    # def get_time_taken(self):
    #     return self.__time_taken

    def get_SV_time_taken(self):
        return self.__SV_time_taken
    
    def get_SP_time_taken(self):
        return self.__SP_time_taken
    
    def get_nouki_copy(self):
        return self.__nouki_copy
    
    def get_firsts(self):
        return self.__firsts

    def get_no_renzoku_seisan(self):
        return self.__no_renzoku_seisan

    def get_clean_time(self):
        return self.__clean_time
    
    def get_kouyousoka_maya(self):
        return self.__kouyousoka_maya
    
    def get_lasts(self):
        return self.__lasts
    
    def get_last_first(self):
        return self.__last_first

    def get_weight_limit(self):
        return self.__weight_limit

    def get_only_two(self):
        return self.__only_two

    def get_used(self):
        return self.__used

    def get_cleaning_time(self):
        return self.__cleaning_jikan
    
    def get_clean1(self):
        return self.__clean1

    def get_mc_renzo(self):
        return self.__mc_renzo

    # __end_time
    def get_end_time(self):
        return self.__end_time

    def get_st_time(self):
        return self.__st_time
    # __st_time
    
    def get_stretch_flag(self):
        return self.__stretch_flag

    def get_priority(self):
        return self.__priority
    
    def get_nitrogen_gas(self):
        return self.__nitrogen_gas


    def set_priority(self,value):
        self.__priority=value

    def set_nouki_copy(self,nouki):
        self.__nouki_copy=nouki

    def set_used(self,uses):
        self.__used=uses
    
    def set_cleaning_time(self,cleaning_time):
        self.__cleaning_jikan=cleaning_time

    def set_jyounban(self,rank):
        self.__jyounban=rank

    def set_slot(self,before_time,start_time):
        self.__slot=f"{before_time}-->{start_time}"

    def set_slot_removing(self,value):
        self.__slot=None

    def set_seisanbi(self,seisanbi):
        self.__seisanbi=seisanbi

    def set_clean1(self,value):
        self.__clean1=value

    def set_end_time(self,end_time):
        self.__end_time=end_time

    
    def set_st_time(self,value):
        self.__st_time=value

    # def set_stretch_flag(self,value):
    #     self.__stretch_flag=value


class Date_Class:
    def __init__(self,each_date,line_break_pattern):
        self.date=each_date
        self.line_break_pattern = line_break_pattern





class Stretch_Flag_setter:
    def __init__(self,nouki_copy,see_future):
        self.__stretch_flag=1
        # self.__nouki=nouki
        self.__nouki_copy=nouki_copy

        dic_SV={}
        dic_SP={}
        initial=0
        for i in range(see_future+1):
            dic_SV.update({i:initial})
            dic_SP.update({i:initial})


        self.__dict_checking_SV=dic_SV
        self.__dict_checking_SP=dic_SP                #{0:0,1:0,2:0,3:0}

        # self.__break_start_time=break_start_time  #,break_start_time=None,break_duration=None
        # self.__break_duration=break_duration
    
    
    def get_stretch_allowable(self):
        
        return self.__stretch_flag
    
    def set_stretch_allowable(self,value):
        self.__stretch_flag=value

    # def get_nouki_flag(self):
    #     return self.__nouki

    def get_nouki_copy(self):
        return self.__nouki_copy


    def get_dict_SV(self):
        return self.__dict_checking_SV
    
    def get_dict_SP(self):
        return self.__dict_checking_SP

    def set_dict_SV(self,dicts):
        self.__dict_checking_SV=dicts

    def set_dict_SP(self,dicts):
        self.__dict_checking_SP=dicts
    
    