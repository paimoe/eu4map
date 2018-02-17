# from map/climate.txt
WASTELANDS = list(map(int, """2426 1173 1779 1781 1782 1783 1784 1785 1786 1787 1788 1789 1790 1791 1793 1794 1795 1796 1797 1798 1799 1801 1802 1803 1804 1805 1806 1807 1808 1810 1811 1812 1814 1950 2194 2200 2251 2334 2608 2740 2425 2936 3415 3416 3417 3418 3419 3590 3591 3592 3593 3594 3595 3596 3597 3598 3599 3620 3621 3622 3623 3624 3625 3626 3427 3628 3629 3630 3631 3632 3633 3634 3635 3636 3437 3638 3639 4146 4153 4154 4155 4156 4157 4159 4160 4161 4162 4167 4168 4169 4170 4172 4177 4178 4179 4276 4321 4322 4328""".split(' ')))

# Seas and stuff, from map/region.txt
SEAS = 'baltic_area,kattegat_area,north_sea_area,norwegian_sea_area,white_sea_area,celtic_sea_area,english_channel_area,bay_of_biscay_area,north_atlantic_area,denmark_strait_area,sea_of_labrador_area,hudson_bay_sea_area,gulf_of_st_lawrence_area,gulf_stream_area,eastern_mediterrenean_area,western_mediterrenean_area,black_sea_area,bahama_channel_area,coast_of_guyana_area,caribbean_sea_area,gulf_of_mexico_area,sargasso_sea_area,west_african_coast_sea_area,gulf_of_guinea_sea_area,western_indian_ocean_area,swahili_coast_sea_area,arabian_sea_area,persian_gulf_area,red_sea_area,eastern_indian_ocean_area,bay_of_bengal_area,andaman_sea_area,south_indian_ocean_area,java_sea_area,south_china_sea_area,celebes_sea_area,banda_arafura_seas_area,east_china_sea_area,philipine_sea_area,sea_of_japan_area,sea_of_okhotsk_area,east_pacific_ocean_area,coral_sea_area,tasman_sea_area,great_australian_bight_area,south_pacific_area,polynesian_triangle_area,north_pacific_area,north_pacific_coast_area,berring_sea_area,gulf_of_alaska_area,chilean_sea_area,sea_of_grau_area,gulf_of_panama_area,coast_of_brazil_sea_area,argentine_sea_area,south_atlantic_area,skeleton_coast_area,cape_of_storms_area'.split(',')

LAKES = ''

# Need to differentiate between seas and oceans (maybe)
FORMABLES = {
    #'TAG': [<provinces>]
}

RELEASEABLES = {
    #'TAG': 
}

RELIGIONS = {
    'group': {
        'catholic': 'color'
    }
}