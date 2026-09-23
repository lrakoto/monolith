/* keep the original grove and planting intact for the comparison; the new
   garden owns its replacements and can disappear with one parent switch. */
function rememberStudyGrove() {
  buildRedwoods(); GARDEN.original.push(WORLD.redwoods);
}
function rememberStudyStele(seed,x,z,scale) {
  GARDEN.original.push(buildStele(seed,x,z,scale));
  GARDEN.trees.push([seed,x,z,scale]);
}
function rememberStudyPond() {
  buildPondPlanting(); GARDEN.original.push(...WORLD.pondPlanting);
}
function buildGardenStonework() {
  const base=WORLD.studyStairMat;
  if(!base)return;
  const mat=base.clone();mat.roughness=.76;mat.envMapIntensity=.60;
  mat.onBeforeCompile=sh=>{
    sh.vertexShader='varying vec3 vMasonry; varying vec3 vMasonryN;\n'+sh.vertexShader;
    sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
      vMasonry=(modelMatrix*vec4(position,1.)).xyz;
      vMasonryN=normalize(mat3(modelMatrix)*normal);`);
    sh.fragmentShader='varying vec3 vMasonry; varying vec3 vMasonryN;\n'+sh.fragmentShader;
    sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
      float top=smoothstep(.55,.9,abs(vMasonryN.y));
      vec2 stoneUV=mix(vMasonry.xy*vec2(.55,1.65),vMasonry.xz*vec2(.55,.82),top);
      stoneUV.x+=mod(floor(stoneUV.y),2.)*.5;
      vec2 edge=abs(fract(stoneUV)-.5);
      vec2 aa=max(fwidth(stoneUV),vec2(.002));
      vec2 seam=smoothstep(vec2(.485)-aa,vec2(.495)+aa,edge);
      float mortar=max(seam.x,seam.y);
      float block=fract(sin(dot(floor(stoneUV),vec2(127.1,311.7)))*43758.5453);
      float age=.5+.5*sin(vMasonry.x*2.1+sin(vMasonry.z*1.7)+vMasonry.y*.8);
      float moss=smoothstep(5.2,8.2,abs(vMasonry.x))*smoothstep(.65,.92,age)*top;
      diffuseColor.rgb*=mix(.87,1.06,block)*(1.-mortar*.26);
      diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*vec3(.65,.82,.46),moss*.42);`);
  };
  mat.customProgramCacheKey=()=> 'garden-stone-joints-1';
  scene.traverse(o=>{if(o.isMesh && o.material===base)gardenEdit(o,'material',mat);});
}
function buildWoodlandUnderstory() {
  if(GARDEN_STYLE==='temple')return;
  const rnd=mulberry32(GARDEN_STYLE==='forest'?4810:4811),matrix=new THREE.Matrix4(),q=new THREE.Quaternion();
  const mat=gardenWind(new THREE.MeshStandardMaterial({color:0x81985d,side:THREE.DoubleSide,roughness:.86,envMapIntensity:.7}),.14,true);
  const mesh=new THREE.InstancedMesh(GARDEN.leafGeo,mat,LOW?650:1800),color=new THREE.Color();
  let count=0;
  for(let i=0;i<mesh.count*3 && count<mesh.count;i++){
    const side=i%2?1:-1,cluster=Math.floor(i/24),angle=rnd()*TAU;
    const cx=side*(9+Math.sin(cluster*8.3)*2.3+Math.floor(cluster/8)*.7),cz=-3-(cluster%15)*2.1;
    const x=cx+Math.cos(angle)*rnd()*1.3,z=cz+Math.sin(angle)*rnd()*1.3,y=gardenGround(x,z);
    if(y<.02)continue;
    q.setFromEuler(new THREE.Euler(-.45+rnd()*1.1,rnd()*TAU,(rnd()-.5)*1.8));
    const size=.22+rnd()*.30;
    matrix.compose(new THREE.Vector3(x,y+.10+rnd()*.65,z),q,new THREE.Vector3(size,size*1.3,size));mesh.setMatrixAt(count,matrix);
    color.setHSL(.23+rnd()*.06,.25+rnd()*.15,.22+rnd()*.14);mesh.setColorAt(count++,color);
  }
  mesh.count=count;mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor.needsUpdate=true;
  mesh.receiveShadow=true;mesh.frustumCulled=false;mesh.name='woodland understory leaves';GARDEN.group.add(mesh);
  /* a single fallen limb interrupts the planted bank, well away from the
     central reflection; broken ends stay dark instead of becoming white discs. */
  const log=new THREE.Mesh(new THREE.CylinderGeometry(.24,.34,4.8,LOW?9:16,3),GARDEN.bark);
  log.rotation.set(.16,0,1.34);log.position.set(-12.8,gardenGround(-12.8,-6.3)+.34,-6.3);
  log.castShadow=true;log.receiveShadow=true;log.name='fallen bank limb';GARDEN.group.add(log);
}

function buildGardenRedwoods() {
  const bark = surface(lib('redwoodBark', texRedwoodBark), [1, 1],
    { color: 0x827669, roughness: .96, normal: .72, metalness: 0, env: .55 });
  const needles = new THREE.MeshStandardMaterial({ color: 0x465b47, roughness: .94,
    metalness: 0, side: THREE.DoubleSide, envMapIntensity: .65 });
  const groveTime = WET_TIME;
  gardenSurface(bark, 'bark');
  needles.onBeforeCompile = sh => {
    sh.uniforms.uBreeze = groveTime;
    sh.vertexShader = 'uniform float uBreeze;\n' + sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\n' +
      'vec3 base=(instanceMatrix*vec4(0.,0.,0.,1.)).xyz;\n' +
      'float ph=base.x*.31+base.z*.23+base.y*.19;\n' +
      'float tip=pow(clamp(position.z,0.,1.),1.3);\n' +
      'transformed.x+=(sin(uBreeze*.64+ph)*.065+sin(uBreeze*3.1+ph*2.)*.032)*tip;\n' +
      'transformed.y+=cos(uBreeze*.51+ph)*.048*tip;\n');
  };
  gardenSway(bark,8,38,.25);gardenSway(needles,8,38,.25);
  const woodParts = [], sprays = [], specs = [
    [71, 13.4, -13.0, 1.05, 43, 1.72], [72, -12.8, -9.4, .95, 46, 1.82],
    [73, 10.0, -19.0, .90, 36, 1.44], [74, -15.5, -17.5, 1.0, 44, 1.65],
    [75, 18.0, -6.0, .88, 49, 1.96],
    [81, -23, -40, 1, 46, 1.45, true], [82, 24, -45, 1, 50, 1.60, true],
    [83, -32, -61, 1, 56, 1.80, true], [84, 34, -65, 1, 58, 1.70, true],
    [85, -15, -60, 1, 43, 1.28, true], [86, 16, -68, 1, 51, 1.40, true],
    [87, -42, -74, 1, 60, 1.75, true], [88, 44, -79, 1, 63, 1.90, true]
  ].filter((_, i) => !LOW || i < 9);
  const up = new THREE.Vector3(0, 1, 0), orient = new THREE.Quaternion();
  const twig = (a, b, ra, rb) => {
    const d = b.clone().sub(a), len = d.length();
    orient.setFromUnitVectors(up, d.normalize());
    const geo = new THREE.CylinderGeometry(rb, ra, len, LOW ? 5 : 7, 1, true);
    geo.applyQuaternion(orient).translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2);
    return geo;
  };
  specs.forEach(([seed, x, z, scale, height, radius, distant]) => {
    const rnd = mulberry32(seed), parts = [redwoodTrunkGeo(height, radius, seed, distant)];
    const trunkRnd = mulberry32(seed); trunkRnd();
    const lean = (trunkRnd() - .5) * .8;
    const world = new THREE.Matrix4().makeScale(scale, scale, scale); world.setPosition(x, distant ? PODIUM : 0, z);
    const point = (a, distance, y) => {
      const t = clamp(y / height, 0, 1);
      const p = new THREE.Vector3(Math.cos(a) * distance + Math.sin(t * 2.4) * lean,
        y, Math.sin(a) * distance + Math.sin(t * 3.6) * .24);
      /* the inner tree's low limbs stay clear of the stair and the slot. */
      if (y * scale < 20 && Math.abs(x + p.x * scale) < 7.3)
        p.x = (Math.sign(x) * 7.3 - x) / scale;
      return p;
    };
    /* broken low limbs and flared roots tell the scale before the canopy
       enters the frame. they taper to the ground rather than sitting on it. */
    for (let i = 0; i < (distant ? 0 : 7); i++) {
      const a = i / 7 * TAU + rnd() * .25;
      const a0 = point(a, radius * .65, 1.1 + rnd() * .6);
      const a1 = point(a, radius * 1.42, .36);
      const a2 = point(a + .1, radius * (1.9 + rnd() * .35), -.025);
      parts.push(twig(a0, a1, .31, .19), twig(a1, a2, .19, .015));
    }
    for (let i = 0; i < (distant ? 2 : 6); i++) {
      const a = rnd() * TAU, y = height * (.16 + rnd() * .24);
      const a0 = point(a, radius * .65, y), a1 = point(a, radius + .7 + rnd() * .6, y + .2);
      parts.push(twig(a0, a1, .17, .055));
    }
    const branches = distant ? (LOW ? 6 : 10) : (LOW ? 16 : 28);
    for (let i = 0; i < branches; i++) {
      const t = .27 + i / (branches - 1) * .69, y = height * t + (rnd() - .5) * .7;
      const a = i * 2.39996 + rnd() * .65 + seed;
      const length = (1.0 + 4.8 * Math.pow(1 - t, .65)) * (.76 + rnd() * .36);
      const p0 = point(a, radius * (1 - t) * .60, y);
      const drop = .25 + rnd() * .80;
      const p1 = point(a, length * .38, y - drop);
      const p2 = point(a + .07, length * .76, y - drop * .62);
      const p3 = point(a + .13, length, y + .38 + rnd() * .5);
      const thickness = .17 * (1 - t) + .028;
      parts.push(twig(p0, p1, thickness, thickness * .72),
        twig(p1, p2, thickness * .72, thickness * .40), twig(p2, p3, thickness * .40, .012));
      const leafCount = distant ? (LOW ? 2 : 3) : (LOW ? 6 : 10);
      for (let j = 0; j < leafCount; j++) {
        const u = .14 + j / (leafCount - 1) * .82;
        const centre = p1.clone().lerp(p3, u);
        const s = j % 2 ? -1 : 1;
        const side = new THREE.Vector3(-Math.sin(a), .05, Math.cos(a));
        const tip = centre.clone().addScaledVector(side, s * (.35 + rnd() * .65) * (1 - u * .55));
        parts.push(twig(centre, tip, .022, .007));
        const obj = new THREE.Object3D();
        obj.position.copy(tip).applyMatrix4(world);
        obj.rotation.set((rnd() - .5) * 1.05, -a + s * .9 + (rnd() - .5) * .45, (rnd() - .5) * .80);
        const leafScale = scale * (1.35 + rnd() * .80) * (1.1 - t * .35);
        obj.scale.set(leafScale, leafScale, leafScale * (1.15 + rnd() * .5)); obj.updateMatrix();
        sprays.push({ matrix: obj.matrix.clone(), color: new THREE.Color().setHSL(.27 + rnd() * .055, .17 + rnd() * .08, .50 + rnd() * .22) });
      }
    }
    parts.forEach(geo => woodParts.push(geo.applyMatrix4(world)));
  });
  const group = new THREE.Group(); group.name = 'detailed redwood grove';
  const wood = new THREE.Mesh(mergeGeos(woodParts), bark);
  wood.name = 'redwood-trunks-and-boughs'; wood.castShadow = true; wood.receiveShadow = true; group.add(wood);
  const foliage = new THREE.InstancedMesh(redwoodSprayGeo(), needles, sprays.length);
  foliage.name = 'redwood-needle-sprays';
  sprays.forEach((s, i) => { foliage.setMatrixAt(i, s.matrix); foliage.setColorAt(i, s.color); });
  foliage.instanceMatrix.needsUpdate = true; foliage.instanceColor.needsUpdate = true;
  foliage.receiveShadow = true; foliage.frustumCulled = false; group.add(foliage);
  /* two draw calls for the grove; needle shadows at this distance only make
     the static shadow map noisy, while the solid boughs carry its silhouette. */
  GARDEN.group.add(group);
}
