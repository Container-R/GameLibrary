"""Literal finite experiment contract. No native imports or runtime discovery."""
CASES = [
    {'id':'inverse-reference','model':0xD002,'maximum':10,'distance':1,'ratio':1.0},
    {'id':'inverse-max','model':0xD002,'maximum':10,'distance':10,'ratio':0.1},
    {'id':'inverse-beyond','model':0xD002,'maximum':10,'distance':20,'ratio':0.1},
    {'id':'inverse-short-max','model':0xD002,'maximum':5,'distance':20,'ratio':0.2},
    {'id':'linear-max','model':0xD004,'maximum':10,'distance':10,'ratio':0.0},
]
PARTS = ('warmup','window1','window2')
FORMAT = {'frequency':48000,'channels':0x1500,'type':0x1406,'hrtf':0,'limiter':0}
LISTENER = {'gain':1.0,'position':[0.0,0.0,0.0],'velocity':[0.0,0.0,0.0],
            'orientation':[0.0,0.0,-1.0,0.0,1.0,0.0]}
SOURCE_FLOATS = [('pitch',0x1003,1.0),('gain',0x100A,1.0),('min_gain',0x100D,0.0),
                 ('max_gain',0x100E,1.0),('reference',0x1020,1.0),('rolloff',0x1021,1.0),
                 ('cone_inner',0x1001,360.0),('cone_outer',0x1002,360.0),('cone_outer_gain',0x1022,1.0)]
SOURCE_INTS = [('relative',0x202,0),('looping',0x1007,1)]
SOURCE_VECTORS = [('velocity',0x1006,[0.0,0.0,0.0]),('direction',0x1005,[0.0,0.0,0.0])]
BUFFER = {'frequency':48000,'bits':16,'channels':1,'size':96}
VERSION = '1.1 ALSOFT 1.24.2'
BEGIN = {'schema':1,'configuration_fully_excluded':False,'case_count':5,'sample_rate':48000,
         'frame_count_per_part':4800,'parts_per_case':3,'sample_format':'float32-le',
         'pcm_format':'s16-le','pcm_positive_count':24,'pcm_negative_count':24,'pcm_amplitude':1024,
         'default_processing_basis':'new_source_no_EFX_EAX_changes_fixed_source_not_getter',
         'ordinary_device_calls':0,'capture_calls':0,'effect_calls':0}
GLOBAL_CHECKS = ['initial_alc','loopback_extension','resolve_open','resolve_format','resolve_render']

def source_values(case):
    return {**{k:v for k,_,v in SOURCE_FLOATS}, **{k:v for k,_,v in SOURCE_INTS},
            **{k:v for k,_,v in SOURCE_VECTORS}, 'maximum':float(case['maximum']),
            'position':[0.0,0.0,-float(case['distance'])], 'type':0x1028,'state':0x1011,'sample_offset':0}

def ready_checks():
    names = ['loopback_open','hrtf_extension','limiter_extension','format_supported','create_context',
             'make_current','initial_al','get_version','get_renderer']
    names += ['get_format_'+x for x in FORMAT] + ['get_hrtf_status']
    names += ['gen_buffer','buffer_data'] + ['get_buffer_'+x for x in BUFFER]
    names += ['gen_source','set_source_buffer','get_source_buffer']
    for k in LISTENER: names += ['set_listener_'+k,'get_listener_'+k]
    for k,_,_ in SOURCE_FLOATS: names += ['set_source_'+k,'get_source_'+k]
    names += ['set_source_maximum','get_source_maximum']
    for k,_,_ in SOURCE_INTS: names += ['set_source_'+k,'get_source_'+k]
    for k,_,_ in SOURCE_VECTORS: names += ['set_source_'+k,'get_source_'+k]
    names += ['set_source_position','get_source_position','set_distance_model','get_distance_model',
              'get_source_type','get_source_state','get_source_sample_offset']
    return names
CLEANUP_CHECKS = ['stop','get_stopped','detach_buffer','get_detached_buffer','delete_source',
                  'delete_buffer','detach_context','destroy_context','close_loopback']
