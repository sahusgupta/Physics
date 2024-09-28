import React, { useEffect, useRef, useState } from 'react';
import { Engine, Render, World, Bodies, Runner } from 'matter-js';
import { Button, Slider, Typography, Box, Container, Paper } from '@mui/material';

const PhysicsPlayground = () => {
  const scene = useRef(null);
  const engine = useRef(Engine.create());
  const [gravity, setGravity] = useState(1);
  const [timeScale, setTimeScale] = useState(1);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const cw = 800;
    const ch = 600;

    const render = Render.create({
      element: scene.current,
      engine: engine.current,
      options: {
        width: cw,
        height: ch,
        wireframes: false,
        background: '#f0f0f0'
      }
    });

    World.add(engine.current.world, [
      Bodies.rectangle(cw / 2, ch + 50, cw + 100, 100, { isStatic: true }),
      Bodies.rectangle(-50, ch / 2, 100, ch + 100, { isStatic: true }),
      Bodies.rectangle(cw + 50, ch / 2, 100, ch + 100, { isStatic: true })
    ]);

    Render.run(render);
    const runner = Runner.create();

    return () => {
      Render.stop(render);
      World.clear(engine.current.world);
      Engine.clear(engine.current);
      render.canvas.remove();
      render.canvas = null;
      render.context = null;
      render.textures = {};
    };
  }, []);

  useEffect(() => {
    engine.current.world.gravity.y = gravity;
  }, [gravity]);

  useEffect(() => {
    engine.current.timing.timeScale = timeScale;
  }, [timeScale]);

  useEffect(() => {
    if (isPaused) {
      Runner.stop(engine.current);
    } else {
      Runner.run(engine.current);
    }
  }, [isPaused]);

  const handleAddCircle = () => {
    const circle = Bodies.circle(
      Math.random() * 780 + 10,
      Math.random() * 580 + 10,
      Math.random() * 20 + 10,
      {
        restitution: 0.8,
        render: {
          fillStyle: `rgb(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255})`
        }
      }
    );
    World.add(engine.current.world, circle);
  };

  const handleAddRectangle = () => {
    const rectangle = Bodies.rectangle(
      Math.random() * 780 + 10,
      Math.random() * 580 + 10,
      Math.random() * 50 + 10,
      Math.random() * 50 + 10,
      {
        restitution: 0.8,
        render: {
          fillStyle: `rgb(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255})`
        }
      }
    );
    World.add(engine.current.world, rectangle);
  };

  const handleReset = () => {
    World.clear(engine.current.world, true);
    World.add(engine.current.world, [
      Bodies.rectangle(400, 650, 900, 100, { isStatic: true }),
      Bodies.rectangle(-50, 300, 100, 700, { isStatic: true }),
      Bodies.rectangle(850, 300, 100, 700, { isStatic: true })
    ]);
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Physics Playground
      </Typography>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ mb: 2 }}>
          <Button variant="contained" onClick={handleAddCircle} sx={{ mr: 1 }}>
            Add Circle
          </Button>
          <Button variant="contained" onClick={handleAddRectangle} sx={{ mr: 1 }}>
            Add Rectangle
          </Button>
          <Button variant="contained" onClick={handleReset} sx={{ mr: 1 }}>
            Reset
          </Button>
          <Button variant="contained" onClick={() => setIsPaused(!isPaused)}>
            {isPaused ? 'Resume' : 'Pause'}
          </Button>
        </Box>
        <Box sx={{ mb: 2 }}>
          <Typography gutterBottom>Gravity</Typography>
          <Slider
            value={gravity}
            onChange={(_, newValue) => setGravity(newValue)}
            min={-2}
            max={2}
            step={0.1}
            valueLabelDisplay="auto"
          />
        </Box>
        <Box>
          <Typography gutterBottom>Time Scale</Typography>
          <Slider
            value={timeScale}
            onChange={(_, newValue) => setTimeScale(newValue)}
            min={0}
            max={2}
            step={0.1}
            valueLabelDisplay="auto"
          />
        </Box>
      </Paper>
      <div ref={scene} style={{ width: '800px', height: '600px' }} />
    </Container>
  );
};

export default PhysicsPlayground;