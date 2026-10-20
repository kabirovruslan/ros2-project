import os
import yaml
import random

color_dict = {
    0: [0.0, 0.068, 0.325],    # синий
    1: [0.93, 0.2, 0.007],  # оранжевый
    2: [0.0, 0.0, 0.0]   # черный
}
combinations_dict={
    0: (0,0,0,0),
    1: (0,0,0,1),
    2: (0,0,1,0),
    3: (0,0,1,1),#
    4: (0,1,0,0),
    5: (0,1,0,1),#
    6: (0,1,1,0),#
    7: (0,1,1,1),
    8: (1,0,0,0),
    9: (1,0,0,1),#
    10: (1,0,1,0),#
    11: (1,0,1,1),
    12: (1,1,0,0),#
    13: (1,1,0,1),
    14: (1,1,1,0),
    15: (1,1,1,1),

    #16: {2,2}# для черных грузов

}



def create_cargo_positions(input_path, output_path):
    ''' Code for generation sdf file with cargoes'''
    long, wide, height = 0.15, 0.05, 0.03
    with open(input_path, 'r') as f:
        config = yaml.safe_load(f)

    
    sdf_content = '''<?xml version="1.0"?>
<sdf version="1.10">
  <model name="all_cargo">
'''
    
    group=0
    for group_name, group_data in config.items():
        
        if group_name=="randomize": continue
        if not group_data.get('active', True): continue
        
        if config.get('randomize', True):
            two_ones_index=(3,5,6,9,10,12)
            color_combination=combinations_dict.get(random.choice(two_ones_index))
        else:
            color_combination=combinations_dict.get(group_data['is_color'])

        
        if len(group_data['coords']) >= 6:
            group+=1
            x, y, z, x_rot, y_rot, z_rot = group_data['coords']
            
            if z_rot != 0: 
                x -= 0.075
            else: 
                y -= 0.075
                

            sdf_content += f'''    <model name='group_{group}'>\n'''

            for i in range(group_data['elements']):
                if i < len(color_combination):
                    color_index = color_combination[i]
                else:
                    color_index = 0  
                    
                color = color_dict.get(color_index)
                
                r_emiss = 0.2 if (color_index == 1) else 0
                
                red, green, blue = color
                sdf_content += f'''
      <model name='cargo_{group}_{i+1}'>
        <pose>{x:.3f} {y:.3f} {z:.3f} {x_rot} {y_rot} {z_rot}</pose>
        <link name='grip_link_{group}_{i+1}'>
          <inertial>
            <inertia>
              <ixx>2.98e-4</ixx>
              <ixy>0</ixy>
              <ixz>0</ixz>
              <iyy>4.67e-3</iyy>
              <iyz>0</iyz>
              <izz>4.95e-3</izz>
            </inertia>
            <mass>0.35</mass>
            <pose>0 0 0 0 0 0</pose>
          </inertial>
          <collision name='box_collision_{group}_{i+1}'>
            <geometry>
              <box>
                <size>{long} {wide} {height}</size>
              </box>
            </geometry>
            <surface>
              <friction>
                <ode/>
              </friction>
              <bounce/>
              <contact/>
            </surface>
          </collision>
          <visual name='box_visual_{group}_{i+1}'>
            <geometry>
              <box>
                <size>{long} {wide} {height}</size>
              </box>
            </geometry>
            <material>
              <ambient> {red} {green} {blue} 1</ambient>
              <diffuse> {red} {green} {blue} 1</diffuse>
              <specular>0 0 0 1</specular>
              <emissive>{r_emiss} 0.05 0.0  1</emissive>
            </material>
            <gamma_correction>false</gamma_correction>
          </visual>
          <pose>0 0 0 0 0 0</pose>
          <enable_wind>false</enable_wind>
        </link>
        <static>false</static>
      </model>'''
                print(x,y,z, group)
                if z_rot != 0: 
                    x += 0.05
                else: 
                    y += 0.05

            sdf_content += f'\n    </model>'
    
    sdf_content += '\n  </model>\n</sdf>'
    
    with open(output_path, 'w') as f:
        f.write(sdf_content)
    
    print(f'Successfully created {group} cargo groups in {output_path}')

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    positions_path = os.path.join(base_dir, 'positions.yaml')
    output_path = os.path.join(base_dir, 'cargoes.sdf')
    
    create_cargo_positions(positions_path, output_path)