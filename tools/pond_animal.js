/* a small doe stays on the dry left bank. cursor rays invite her closer;
   they never drag her through the water or snap her head around. */
function buildPondAnimal(){
  const root=new THREE.Group();root.name='pond deer';GARDEN.group.add(root);
  const coat=new THREE.MeshStandardMaterial({color:0xb08c61,roughness:.92});
  const cream=new THREE.MeshStandardMaterial({color:0xc8b999,roughness:.95});
  const dark=new THREE.MeshStandardMaterial({color:0x171b16,roughness:.48});
  function oval(parent,mat,x,y,z,sx,sy,sz){
    const m=new THREE.Mesh(new THREE.SphereGeometry(1,LOW?8:12,LOW?6:8),mat);
    m.position.set(x,y,z);m.scale.set(sx,sy,sz);m.castShadow=false;m.receiveShadow=true;parent.add(m);return m;
  }
  const body=new THREE.Group();root.add(body);
  oval(body,coat,0,1.05,0,.33,.43,.70);
  oval(body,cream,0,.91,.08,.27,.27,.52);
  const neck=oval(body,coat,0,1.50,.48,.23,.52,.25);neck.rotation.x=.29;
  const head=new THREE.Group();head.position.set(0,1.94,.59);body.add(head);
  oval(head,coat,0,0,.10,.22,.25,.36);
  oval(head,cream,0,-.12,.33,.15,.12,.22);
  oval(head,dark,0,-.06,.49,.12,.085,.07);
  for(const side of [-1,1]){
    const ear=oval(head,coat,side*.21,.32,-.08,.115,.30,.075);ear.rotation.z=-side*.40;
    oval(head,dark,side*.195,.055,.19,.037,.043,.043);
  }
  const tail=oval(body,cream,0,1.27,-.67,.11,.21,.10);tail.rotation.x=-.7;
  const legs=[];
  for(const x of [-.23,.23])for(const z of [-.45,.43]){
    const hip=new THREE.Group();hip.position.set(x,.94,z);root.add(hip);
    oval(hip,coat,0,-.22,0,.075,.27,.085);
    const knee=new THREE.Group();knee.position.y=-.43;hip.add(knee);
    oval(knee,coat,0,-.21,0,.045,.24,.05);
    oval(knee,dark,0,-.43,.035,.065,.065,.10);
    legs.push({hip,knee,phase:(x*z>0?0:Math.PI)+(z<0?.35:0)});
  }
  root.position.set(-11.7,gardenGround(-11.7,-11),-11);root.rotation.y=-.7;root.scale.setScalar(1.15);
  GARDEN.animal={root,body,head,tail,legs,phase:0,speed:0,last:WET_TIME.value,
    target:new THREE.Vector3(-11.7,0,-11),ray:new THREE.Raycaster(),plane:new THREE.Plane(new THREE.Vector3(0,1,0),0),hit:new THREE.Vector3(),look:new THREE.Vector3(),next:0};
}
function updatePondAnimal(){
  const a=GARDEN.animal;if(!a)return;
  const now=WET_TIME.value,dt=Math.min(.05,Math.max(0,now-a.last));a.last=now;
  if(!GARDEN.active || !dt)return;
  const pos=a.root.position;
  const pointer=typeof RIG!=='undefined' && RIG.pointer && typeof COARSE!=='undefined' && !COARSE;
  let invite=false;
  if(pointer){
    a.ray.setFromCamera(new THREE.Vector2(RIG.tmx,RIG.tmy),camera);
    const hit=a.ray.ray.intersectPlane(a.plane,a.hit);
    invite=!!hit && a.ray.ray.direction.y<-.035 && Math.abs(hit.x+11.7)<5 && Math.abs(hit.z+11)<7;
    if(invite){
      const dx=a.hit.x+11.7,dz=a.hit.z+11,r=Math.max(1,Math.hypot(dx/.55,dz/1.5));
      a.target.set(-11.7+dx/r,0,-11+dz/r);a.next=now+3;
    }
    a.ray.ray.at(Math.max(3,camera.position.distanceTo(pos)),a.look);
  }
  if(!invite && now>a.next){
    const angle=now*.37;a.target.set(-11.7+Math.sin(angle)*.55,0,-11+Math.cos(angle)*1.5);a.next=now+7;
  }
  const dx=a.target.x-pos.x,dz=a.target.z-pos.z,d=Math.hypot(dx,dz);
  const heading=Math.atan2(dx,dz),delta=Math.atan2(Math.sin(heading-a.root.rotation.y),Math.cos(heading-a.root.rotation.y));
  if(d>.30)a.root.rotation.y+=Math.max(-dt*.85,Math.min(dt*.85,delta));
  const desired=d>.65?Math.min(.58,(d-.65)*.65)*Math.max(0,Math.cos(delta)):0;
  a.speed+=(desired-a.speed)*(1-Math.exp(-dt*3));
  const nx=pos.x+Math.sin(a.root.rotation.y)*a.speed*dt,nz=pos.z+Math.cos(a.root.rotation.y)*a.speed*dt;
  if(gardenGround(nx,nz)>.06 && Math.hypot((nx+11.7)/.8,(nz+11)/1.8)<1){pos.x=nx;pos.z=nz;}
  else a.speed=0;
  pos.y=gardenGround(pos.x,pos.z)+.015;
  a.phase+=a.speed*dt*5.4;
  const gait=Math.min(1,a.speed/.4);
  a.legs.forEach(l=>{l.hip.rotation.x=Math.sin(a.phase+l.phase)*.40*gait;l.knee.rotation.x=Math.max(0,-Math.sin(a.phase+l.phase))*.45*gait;});
  a.body.position.y=Math.cos(a.phase*2)*.018*gait+Math.sin(now*1.6)*.008;
  let yaw=0,pitch=.10+Math.sin(now*.6)*.05;
  if(pointer){
    const v=a.look.clone().sub(pos);yaw=Math.atan2(v.x,v.z)-a.root.rotation.y;
    yaw=Math.max(-.85,Math.min(.85,Math.atan2(Math.sin(yaw),Math.cos(yaw))));
    pitch=Math.max(-.4,Math.min(.35,-Math.atan2(v.y-1.94,Math.hypot(v.x,v.z))));
  }
  const ease=1-Math.exp(-dt*3.2);a.head.rotation.y+=(yaw-a.head.rotation.y)*ease;a.head.rotation.x+=(pitch-a.head.rotation.x)*ease;
  a.tail.rotation.z=Math.sin(now*1.2)*.075;
}
