import pandas as pd
from datetime import datetime, timedelta
import Record_finder  # Ensure this module is accessible

def stretch_allowable_two_args(original_record, copy_records, flag_object, elements, remaining_time, dates):
    if elements.day_name() == 'Sunday' or elements.day_name() == 'Saturday':
        cleaning_time = 30
    else:
        cleaning_time = 20

    for record in copy_records:
        if record.get_stretch_flag() == 1:
            for flag_setter in flag_object:
                if flag_setter.get_nouki_copy() == elements:
                    dictcon = getattr(flag_setter,f'get_dict_{line}')()
                    dates_range_list = [el for el in dates if el <= record.get_nouki_copy() and el > flag_setter.get_nouki_copy()]
                    day_key = len(dates_range_list)
                    dictcon[day_key] = dictcon.get(day_key, 0) + 1

                    acceptable = True
                    total_stretch_numbers = sum(dictcon.values())
                    if total_stretch_numbers > len(dictcon):
                        acceptable = False

                    variant = 0
                    for loop_counter in range(len(dictcon)):
                        if dictcon[loop_counter] > loop_counter + 1:
                            acceptable = False
                            break

                        if dictcon[loop_counter] == loop_counter + 1:
                            for inner_loop in range(loop_counter + 1, len(dictcon)):
                                if dictcon[inner_loop] >= inner_loop - variant + 1:
                                    acceptable = False
                                    break
                            variant += 1
                            if not acceptable:
                                break

                    if not acceptable:
                        original_record.remove(record)
                        record.set_end_time(record.get_nouki_copy())
                        record.set_st_time(None)
                        record.set_used(0)
                        remaining_time += record.get_cleaning_time() + getattr(record,f'get_{line}_time_taken')() + cleaning_time
                    else:
                        getattr(flag_setter,f'set_dict_{line}')(dictcon)

    return original_record, remaining_time

def check_weight_limit(remaining_time, elements, Class_Data, current_ele):
    if elements.day_name() == 'Sunday' or elements.day_name() == 'Saturday':
        cleaning_time = 30
        total_time = 860
    else:
        cleaning_time = 20
        total_time = 900

    current_start_time = total_time - remaining_time
    eligible_start_time = elements + timedelta(minutes=440) + timedelta(minutes=current_start_time)
    previous_day_start_time = eligible_start_time - timedelta(hours=24)

    weight = sum(ele.get_yotei_syourou() for ele in Class_Data if ele.get_used() == 1 and ele.get_weight_limit() == 1 and ele.get_end_time() >= previous_day_start_time)
    weight += current_ele.get_yotei_syourou()

    current_ele_set_end_time = eligible_start_time + timedelta(minutes=current_ele.get_cleaning_time() + current_getattr(ele,f'get_{line}_time_taken')() + cleaning_time)

    return weight < 51000, current_ele_set_end_time

def allocate_non_priority_records(remaining_time, future_with_today, non_prior_list, elements, Class_Data, flag_object, dates, future_with_today_special):
    if elements.day_name() == 'Sunday' or elements.day_name() == 'Saturday':
        cleaning_time = 30
        total_time = 860
    else:
        cleaning_time = 20
        total_time = 900

    non_prior_list1 = []
    time_used_by_tempahin = 0
    reference_remaining_time = remaining_time

    while remaining_time > 0:
        for ele in future_with_today:
            non_prior_list2 = []
            if remaining_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - cleaning_time > 0:
                if ele.get_weight_limit() == 1 and ele.get_used() == 0 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
                    bools, eligible_start_time = check_weight_limit(remaining_time, elements, Class_Data, ele)
                    if bools:
                        ele.set_used(1)
                        non_prior_list2.append(ele)
                        ele.set_st_time(eligible_start_time)
                        remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + cleaning_time
                        non_prior_list2, remaining_time = stretch_allowable_two_args(non_prior_list2, non_prior_list2, flag_object, elements, remaining_time, dates)
                        non_prior_list1.extend(non_prior_list2)
                        if non_prior_list2:
                            time_used_by_tempahin += ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + cleaning_time
        remaining_time -= 20

    inbetween_time = 0
    if non_prior_list1:
        first_element_non_prior_list = non_prior_list1[0].get_st_time()
        startable_time = total_time - reference_remaining_time
        starting_time_for_now_records = elements + timedelta(minutes=440) + timedelta(minutes=startable_time)
        inbetween_time = (first_element_non_prior_list - starting_time_for_now_records).total_seconds() / 60

    reference_inbetween_time = inbetween_time
    non_prior_lister = []
    for ele in future_with_today_special:
        spel = []
        if ele not in non_prior_list and ele not in non_prior_list1 and ele not in non_prior_lister:
            if ele.get_used() == 0 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
                if inbetween_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - cleaning_time > 0:
                    ele.set_used(1)
                    spel.append(ele)
                    inbetween_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + cleaning_time
                    spel, inbetween_time = stretch_allowable_two_args(spel, spel, flag_object, elements, inbetween_time, dates)
                    if spel:
                        non_prior_lister.append(ele)

    final_remaining_time = reference_remaining_time - reference_inbetween_time - time_used_by_tempahin
    final_non_prior_list = []

    for ele in future_with_today_special:
        spelll = []
        if ele not in final_non_prior_list and ele not in non_prior_lister and ele.get_used() == 0 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
            if final_remaining_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - cleaning_time > 0:
                ele.set_used(1)
                spelll.append(ele)
                final_remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + cleaning_time
                spelll, final_remaining_time = stretch_allowable_two_args(spelll, spelll, flag_object, elements, final_remaining_time, dates)
                if spelll:
                    final_non_prior_list.append(ele)

    return non_prior_list + non_prior_lister + non_prior_list1 + final_non_prior_list

def get_today_first_records(today_data, future_with_today, future_with_today1):
    today_first_records = Record_finder.first_record_finder(today_data, types='KI(テンパー品)')
    if today_first_records:
        for i, ele in enumerate(today_first_records):
            ele.set_cleaning_time(60 if i == 0 else 0)
    else:
        today_first_records = Record_finder.first_record_finder_three(today_data, types='MCｼｮｰﾄ')
        if today_first_records:
            mc_record = Record_finder.first_record_finder_renzoku(today_data, type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
            today_first_records.extend(mc_record)
        else:
            today_first_records = Record_finder.first_record_finder_two(today_data, types='初回限定')
            if not today_first_records:
                today_first_records = Record_finder.first_record_finder_two(today_data, types='副原料添加なし初回限定')
                rem_renzoku_record = Record_finder.first_record_finder_three(today_data, types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                for re in rem_renzoku_record:
                    if re not in today_first_records:
                        today_first_records.append(re)


    
    return today_first_records

def get_today_last_records(today_data, future_with_today):
    # Get high iodine value records
    today_last_records = Record_finder.last_record_finder(today_data, types='高')
    rem_jyunko_dekiru = Record_finder.last_record_finder(today_data, types='準高')
    today_last_records.extend(rem_jyunko_dekiru)

    # If no records found, get low iodine value records
    if not today_last_records:
        today_last_records = Record_finder.last_record_finder(today_data, types='低沃素価')

    # If still no records, get allergen B records
    if not today_last_records:
        today_last_records = Record_finder.last_record_finder_two(today_data, types='B')
        rem_arerukon_records = Record_finder.last_record_finder_four_MOS(today_data, types='〇')
        
        # Move specific product to the end
        nep = [tokui_rec for tokui_rec in rem_arerukon_records if tokui_rec.get_syouhin_name() == 'ﾊｲDXﾌｱﾂﾄ(H)']
        for tokui_rec in nep:
            rem_arerukon_records.remove(tokui_rec)
        rem_arerukon_records.extend(nep)
        
        # Add to last records
        today_last_records.extend(rem_arerukon_records)

    # If still no records, get records with '〇' in 'saishu_gentai'
    if not today_last_records:
        today_last_records = Record_finder.last_record_finder_three(today_data, types='〇')

    return today_last_records


def schedule_non_priority_records(remaining_time, non_priority_record, elements, Class_Data):
    if elements.day_name() == 'Sunday' or elements.day_name() == 'Saturday':
        cleaning_time = 30
    else:
        cleaning_time = 20

    non_prior_list = []
    still_not_allocated = []

    for ele in non_priority_record:
        if remaining_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - cleaning_time > 0:
            if ele.get_weight_limit() == 1:
                bools, current_ele_set_end_time = check_weight_limit(remaining_time, elements, Class_Data, ele)
                if bools:
                    ele.set_end_time(current_ele_set_end_time)
                    ele.set_used(1)
                    non_prior_list.append(ele)
                    remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + cleaning_time
                else:
                    still_not_allocated.append(ele)
            else:
                ele.set_used(1)
                non_prior_list.append(ele)
                remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + cleaning_time

    non_prior_list, remaining_time = stretch_allowable_two_args(non_prior_list, non_prior_list, [], elements, remaining_time, [])
    return non_prior_list

def allocate_future_records(remaining_time, future_with_today, future_data, elements, Class_Data, flag_object, dates, future_with_today_special):
    future_non_prior_list = []
    future_non_prior_list1 = []
    future_non_prior_list2 = []

    all_data = [ele for ele in future_with_today if ele.get_used() == 0]

    for ele in all_data:
        if remaining_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - 20 > 0:
            if ele.get_weight_limit() == 1 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
                bools, current_ele_set_end_time = check_weight_limit(remaining_time, elements, Class_Data, ele)
                if bools:
                    ele.set_end_time(current_ele_set_end_time)
                    ele.set_used(1)
                    future_non_prior_list2.append(ele)
                    remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + 20
            elif ele.get_weight_limit() == 0 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
                ele.set_used(1)
                future_non_prior_list2.append(ele)
                remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + 20

    for ele in future_data:
        if remaining_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - 20 > 0:
            if ele.get_weight_limit() == 1 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
                bools, current_ele_set_end_time = check_weight_limit(remaining_time, elements, Class_Data, ele)
                if bools:
                    ele.set_end_time(current_ele_set_end_time)
                    ele.set_used(1)
                    future_non_prior_list.append(ele)
                    remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + 20

    future_non_prior_list = future_non_prior_list2 + future_non_prior_list
    future_non_prior_list, remaining_time = stretch_allowable_two_args(future_non_prior_list, future_non_prior_list, flag_object, elements, remaining_time, dates)

    for ele in future_data:
        if remaining_time - ele.get_cleaning_time() - getattr(ele,f'get_{line}_time_taken')() - 20 > 0 and ele.get_used() == 0:
            if ele.get_weight_limit() == 0 and ele.get_firsts() == 0 and ele.get_lasts() == 0 and ele.get_last_first() == 0:
                ele.set_used(1)
                future_non_prior_list1.append(ele)
                remaining_time -= ele.get_cleaning_time() + getattr(ele,f'get_{line}_time_taken')() + 20

    future_non_prior_list1, remaining_time = stretch_allowable_two_args(future_non_prior_list1, future_non_prior_list1, flag_object, elements, remaining_time, dates)
    future_non_prior_list.extend(future_non_prior_list1)

    return future_non_prior_list

def assign_time_slots(all_records, elements, start_time, total_time, cleaning_time, line_break_start, line_break_duration_list):
    allowable_start_time = start_time + timedelta(minutes=440)
    task_wise_increment = 0
    i = 0
    prev_record = None

    while i < len(all_records):
        record = all_records[i]
        before_before_time = allowable_start_time

        if i == 0:
            before_time = allowable_start_time
            saturday_special_time1 = before_time
            saturday_special_time2 = before_time + timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
        else:
            before_time = allowable_start_time + timedelta(minutes=cleaning_time) + timedelta(minutes=prev_record.get_cleaning_time())

        if record.get_st_time() is not None:
            before_time = record.get_st_time()

        # Adjust for nitrigen gas transition
        if prev_record is not None:
            prev_nitrogen_gas = prev_record.get_nitrogen_gas()
            current_nitrogen_gas = record.get_nitrogen_gas()
            if (prev_nitrogen_gas == '〇' and current_nitrogen_gas != '〇') or (prev_nitrogen_gas != '〇' and current_nitrogen_gas == '〇'):
                before_time += timedelta(minutes=10)
                total_time -= 10
                if total_time < 0:
                    break

        # Adjust for Saturday and Sunday special times
        if elements.day_name() in ['Sunday', 'Saturday']:
            if (saturday_special_time1 - timedelta(minutes=cleaning_time) <= elements + timedelta(hours=17) and saturday_special_time2 > elements + timedelta(hours=17)):
                before_time += timedelta(minutes=20)
            if (saturday_special_time1 - timedelta(minutes=cleaning_time) <= elements + timedelta(hours=11) and saturday_special_time2 > elements + timedelta(hours=11)):
                before_time += timedelta(minutes=20)

        allowable_start_time = before_time + timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
        difference_of_time = allowable_start_time - before_before_time

        # Adjust for breaks
        for index, (duration, break_start) in enumerate(zip(line_break_duration_list, line_break_start)):
            if before_before_time < break_start and allowable_start_time > break_start:
                before_time = break_start + timedelta(minutes=duration)
                allowable_start_time = before_time + difference_of_time

        if allowable_start_time > elements + timedelta(hours=23):
            break

        record.set_slot(before_time, allowable_start_time)
        record.set_end_time(allowable_start_time)
        record.set_seisanbi(elements)
        record.set_used(1)
        task_wise_increment += 1
        record.set_jyounban(task_wise_increment)

        prev_record = record
        saturday_special_time1 = before_time
        saturday_special_time2 = allowable_start_time

        i += 1

    return all_records[:i]

def unused_dataframe(Class_Data, non_final_df, abc):
    non_final_df["nouki_copy"] = None
    unused_class_data = []

    for ele in Class_Data:
        if ele.get_used() == 0:
            non_final_df = non_final_df.append({
                '品目コード': ele.get_syouhin_code(),
                '品名': ele.get_syouhin_name(),
                'ライン': ele.get_line(),
                'ライン名': ele.get_line_name(),
                '入目': ele.get_iri_me(),
                '流速': ele.get_ryousoku(),
                'テンパリング': ele.get_tenpahin(),
                '沃素価': ele.get_yousoka(),
                'KI': ele.get_KI(),
                '初回限定': ele.get_syoukai_gentei(),
                '最終限定': ele.get_saishu_gentei(),
                'リパック': ele.get_stretch(),
                '予定数量': ele.get_yotei_syourou(),
                '納期': ele.get_nouki(),
                'チケットNO': ele.get_ticket_no(),
                '備考': ele.get_bikou(),
                '生産日': ele.get_seisanbi(),
                '順番': ele.get_jyounban(),
                'slot': ele.get_slot(),
                'nouki_copy': ele.get_nouki_copy()
            }, ignore_index=True)
            unused_class_data.append(ele)

    non_final_df.to_csv(f"{abc}_remaining.csv", encoding="utf-8_sig", index=False)
    return unused_class_data

def schedule_manager(Class_Data, dates_with_features, final_df, flag_object, see_future):
    final_df["nouki_copy"] = None
    final_df = pd.DataFrame(columns=['品目コード', '品名', 'ライン', 'ライン名', '入目', '流速', 'テンパリング', '沃素価', 'KI',
                                     '初回限定', '最終限定', 'リパック', '予定数量', '納期', 'チケットNO', '備考',
                                     '生産日', '順番', 'slot', 'nouki_copy', '窒素ガス'])
    dates = [ele.date for ele in dates_with_features]
    prev_Date = None

    for each_elements in dates_with_features:
        elements = each_elements.date

        # Set total_time and cleaning_time based on day
        if elements.day_name() in ['Sunday', 'Saturday']:
            total_time = 860
            cleaning_time = 30
        else:
            total_time = 900
            cleaning_time = 20

        # Handle line breaks
        looping_range = len(each_elements.line_break_pattern['break_pattern'])
        breaks = {}
        line_break_start = []
        line_break_duration_list = []

        if looping_range > 0:
            breaks = each_elements.line_break_pattern['break_pattern']
            total_break_time = 0

            for index in range(looping_range):
                break_time = breaks[f'break{index}']['break']
                break_duration = breaks[f'break{index}']['break_duration']
                total_break_time += break_duration
                line_break_start.append(break_time)
                line_break_duration_list.append(break_duration)

            total_time -= total_break_time

        # Update stretch flags based on previous day's dictionary
        if prev_Date is not None:
            prev_dict = None
            for ele in flag_object:
                if ele.get_nouki_copy() == prev_Date:
                    prev_dict = getattr(ele,f'get_dict_{line}')()
                    break
            if prev_dict is not None:
                for ele in flag_object:
                    if ele.get_nouki_copy() == elements:
                        current_dict = {k: prev_dict.get(k + 1, 0) for k in range(len(prev_dict) - 1)}
                        current_dict[len(prev_dict) - 1] = 0

                        if prev_dict[0] == 0:
                            for curren_len in range(len(current_dict)):
                                if current_dict[curren_len] >= 1:
                                    current_dict[curren_len] -= 1
                                    break
                        getattr(ele,f'set_dict_{line}')(current_dict)

        # Initialize data lists
        today_data = []
        future_data = []
        future_with_today = []
        future_data1 = []
        future_with_today1 = []
        future_with_today_special = []
        start_time = pd.to_datetime(elements)

        # Populate data lists based on dates and conditions
        for rows_data in Class_Data:
            nouki_date = rows_data.get_nouki_copy()
            if rows_data.get_used() == 0:
                if nouki_date == start_time:
                    today_data.append(rows_data)
                elif start_time < nouki_date <= start_time + timedelta(days=see_future):
                    if rows_data.get_mc_renzo() != 1:
                        future_data.append(rows_data)
                    future_with_today.append(rows_data)
                    future_with_today1.append(rows_data)
                elif start_time + timedelta(days=see_future) < nouki_date <= start_time + timedelta(days=see_future + 3):
                    if rows_data.get_syouhin_name() not in ['ｲﾄｳIK-NT(H)', 'ﾊﾟﾈﾘ-PV(13)']:
                        future_with_today_special.append(rows_data)

        # Initialize record lists
        today_first_records = get_today_first_records(today_data, future_with_today, future_with_today1)
        today_last_records = get_today_last_records(today_data, future_with_today)

        # Calculate total time required for first and last records
        total_time_for_today_first_record = sum(
            [rec.get_cleaning_time() + rec.get_time_taken() + cleaning_time for rec in today_first_records])
        total_time_for_today_last_records = sum(
            [rec.get_cleaning_time() + rec.get_time_taken() + cleaning_time for rec in today_last_records])

        # Adjust remaining time
        remaining_time = total_time - total_time_for_today_first_record - total_time_for_today_last_records

        # Initialize non-priority records
        non_priority_record = [rec for rec in today_data if
                               rec.get_used() == 0 and rec.get_firsts() == 0 and rec.get_lasts() == 0 and rec.get_last_first() == 0]

        # Schedule non-priority records
        non_prior_list = schedule_non_priority_records(remaining_time, non_priority_record, elements, Class_Data)

        # Allocate future records if time remains
        future_records_allocated = allocate_future_records(remaining_time, future_with_today, future_data, elements,
                                                           Class_Data, flag_object, dates, future_with_today_special)

        # Combine all records
        all_records = today_first_records + non_prior_list + future_records_allocated + today_last_records

        # Assign time slots to records, considering nitrigen gas transitions
        all_records = assign_time_slots(all_records, elements, start_time, total_time, cleaning_time,
                                        line_break_start, line_break_duration_list)

        # Update previous date
        prev_Date = elements

        # Add scheduled records to final_df
        for ele in all_records:
            final_df = final_df.append({
                '品目コード': ele.get_syouhin_code(),
                '品名': ele.get_syouhin_name(),
                'ライン': ele.get_line(),
                'ライン名': ele.get_line_name(),
                '入目': ele.get_iri_me(),
                '流速': ele.get_ryousoku(),
                'テンパリング': ele.get_tenpahin(),
                '沃素価': ele.get_yousoka(),
                'KI': ele.get_KI(),
                '初回限定': ele.get_syoukai_gentei(),
                '最終限定': ele.get_saishu_gentei(),
                'リパック': ele.get_stretch(),
                '予定数量': ele.get_yotei_syourou(),
                '納期': ele.get_nouki(),
                'チケットNO': ele.get_ticket_no(),
                '備考': ele.get_bikou(),
                '生産日': ele.get_seisanbi(),
                '順番': ele.get_jyounban(),
                'slot': ele.get_slot(),
                'nouki_copy': ele.get_nouki_copy().date(),
                '窒素ガス': ele.get_nitrogen_gas()
            }, ignore_index=True)

    return final_df, Class_Data

# Example usage:
# Assuming you have the necessary data and objects, you can call:
# final_df, Class_Data = schedule_manager(Class_Data, dates_with_features, final_df, flag_object, see_future)