"""Shape a connected forest shoulder without opening the canopy onto bare ground."""
import math
import bpy


def reshape_left_bank(scene, strength=1.0, both=False):
    def displacement(x, y):
        if both and 70 < x < 245 and 90 < y < 375:
            edge=min(1.0,(x-70)/40,(245-x)/50,(y-90)/40,(375-y)/45)
            edge=max(0.0,edge);edge=edge*edge*(3-2*edge)
            along=y-.24*(x-160)
            ridge=14*math.exp(-((along-295)/48)**2-((x-165)/100)**2)
            shoulder=8*math.exp(-((along-125)/40)**2-((x-150)/85)**2)
            valley=17*math.exp(-((along-215)/40)**2-((x-165)/100)**2)
            # lowering this bank exposed the source trunk's straight cut base in the
            # full render. keep the existing cover and form the valley between raised ridges.
            return strength*edge*max(0.0,ridge+shoulder-valley)*3
        # the shore and stair margin stay anchored. move the planted ground with its
        # crowns so a shallow valley reads as forest depth, not exposed smooth terrain.
        if not (-300 < x < -50 and 15 < y < 315):
            return 0.0
        edge=min(1.0,(-x-50)/35,(x+300)/45,(y-15)/45,(315-y)/45)
        edge=max(0.0,edge);edge=edge*edge*(3-2*edge)
        along=y+.32*(x+150)
        upper=17*math.exp(-((along-230)/48)**2-((x+145)/100)**2)
        lower=10*math.exp(-((along-75)/42)**2-((x+175)/100)**2)
        saddle=20*math.exp(-((along-148)/35)**2-((x+150)/110)**2)
        return strength*edge*(upper+lower-saddle)*3

    terrain=bpy.data.objects['simple forest banks']
    terrain.data=terrain.data.copy()
    inverse=terrain.matrix_world.inverted()
    count=0
    for vertex in terrain.data.vertices:
        world=terrain.matrix_world@vertex.co
        delta=displacement(world.x/3,world.y/3)
        if abs(delta)>.001:
            world.z+=delta;vertex.co=inverse@world;count+=1
    terrain.data.update()
    prefixes=('canopy lobe ','fine foliage ','shoreline stand ','shoreline foliage ',
              'sunstruck edge tree ','sunstruck edge foliage ','plinth planting ',
              'branch replacement ')
    moved=[]
    for obj in scene.objects:
        if not obj.name.startswith(prefixes):continue
        delta=displacement(obj.location.x/3,obj.location.y/3)
        if abs(delta)>.001:
            obj.location.z+=delta;moved.append(obj.name)
    assert count>100 and len(moved)>100
    scene['canopy_landform_targets']=','.join(sorted(moved))
    print('Connected forest banks:',count,'terrain vertices;',len(moved),'plants; fixed shore and stair margin',flush=True)
