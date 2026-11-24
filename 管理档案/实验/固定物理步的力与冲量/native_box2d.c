/* Original free-body probe for a pinned Box2D source snapshot. */
#include "box2d/box2d.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

enum { FORCE, FIXED_J, ONCE, DUPLICATE, UPFRONT, FORCE_ONE_TICK, DOUBLE_FORCE, SAMPLES };
static const char* names[SAMPLES] = {
    "force_each_tick", "fixed_impulse_each_tick", "input_event_once",
    "input_event_repeated", "total_impulse_upfront", "force_one_tick", "double_force_first_tick"
};

static void check(double measured, double expected, double tolerance)
{
    if (fabs(measured - expected) > tolerance || !isfinite(measured))
    {
        fprintf(stderr, "native check failed: measured %.8f expected %.8f\n", measured, expected);
        exit(1);
    }
}

static void run(int hz, int substeps)
{
    b2WorldDef worldDef = b2DefaultWorldDef();
    worldDef.gravity = (b2Vec2){0, 0};
    b2WorldId world = b2CreateWorld(&worldDef);
    b2BodyId body[SAMPLES];
    for (int i = 0; i < SAMPLES; ++i)
    {
        b2BodyDef def = b2DefaultBodyDef();
        def.type = b2_dynamicBody;
        def.enableSleep = false;
        body[i] = b2CreateBody(world, &def);
        b2Body_SetMassData(body[i], (b2MassData){ .mass = 2.0f });
        check(b2Body_GetMass(body[i]), 2.0, 1e-7);
    }
    const double k = hz, n = substeps;
    const b2Vec2 force = {12, 0}, stepImpulse = {0.2f, 0}, jump = {4, 0}, total = {12, 0};
    printf("outer_hz=%d internal_substeps=%d simulated_time=1.000 s\n", hz, substeps);
    for (int tick = 0; tick < hz; ++tick)
    {
        b2Body_ApplyForceToCenter(body[FORCE], force, true);
        b2Body_ApplyLinearImpulseToCenter(body[FIXED_J], stepImpulse, true);
        if (tick == 0)
        {
            b2Body_ApplyLinearImpulseToCenter(body[ONCE], jump, true);
            b2Body_ApplyLinearImpulseToCenter(body[UPFRONT], total, true);
            b2Body_ApplyForceToCenter(body[FORCE_ONE_TICK], force, true);
            b2Body_ApplyForceToCenter(body[DOUBLE_FORCE], force, true);
            b2Body_ApplyForceToCenter(body[DOUBLE_FORCE], force, true);
        }
        if (tick < 2)
            b2Body_ApplyLinearImpulseToCenter(body[DUPLICATE], jump, true);
        b2World_Step(world, 1.0f / hz, substeps);
        if (tick == 0)
        {
            double forceX = b2Body_GetPosition(body[FORCE]).x;
            double stepJX = b2Body_GetPosition(body[FIXED_J]).x;
            double forceV = b2Body_GetLinearVelocity(body[FORCE]).x;
            double stepJV = b2Body_GetLinearVelocity(body[FIXED_J]).x;
            printf("step_1 force_v_mps=%.6f force_x_m=%.6f step_J_v_mps=%.6f step_J_x_m=%.6f\n", forceV, forceX, stepJV, stepJX);
            check(forceV, 6.0/k, 1e-7);
            check(stepJV, 0.1, 1e-7);
            check(forceX, (6.0/k/k)*(n+1)/(2*n), 1e-7);
            check(stepJX, 0.1/k, 1e-7);
        }
    }
    double oneX = (6.0 / k) * (1.0 - 0.5/k + 0.5/(k*n));
    double v_expected[SAMPLES] = {6.0, 0.1*k, 2.0, 4.0, 6.0, 6.0/k, 12.0/k};
    double x_expected[SAMPLES] = {3.0+3.0/(k*n), 0.05*(k+1), 2.0, 4.0-2.0/k, 6.0, oneX, 2*oneX};
    for (int i = 0; i < SAMPLES; ++i)
    {
        double v = b2Body_GetLinearVelocity(body[i]).x;
        double x = b2Body_GetPosition(body[i]).x;
        printf("%-24s v_mps=%7.4f x_m=%7.4f\n", names[i], v, x);
        check(v, v_expected[i], 3e-5);
        check(x, x_expected[i], 3e-5);
    }
    b2DestroyWorld(world);
}

int main(void)
{
    for (int hz = 30; hz <= 120; hz *= 2)
        for (int n = 1; n <= 4; n *= 4)
            run(hz, n);
}
