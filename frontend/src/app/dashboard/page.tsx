"use client";

import { Badge } from "@/components/badge";
import { Divider } from "@/components/divider";
import { Heading, Subheading } from "@/components/heading";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/table";
import { getData, getHistoricalEnergyProduction } from "@/data";

import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export function Stat({
  title,
  value,
  change,
}: {
  title: string;
  value: string;
  change: string;
}) {
  return (
    <div>
      <Divider />
      <div className="mt-6 text-lg/6 font-medium sm:text-sm/6">{title}</div>
      <div className="mt-3 text-3xl/8 font-semibold sm:text-2xl/8">
        {value} kwh
      </div>
      <div className="mt-3 text-sm/6 sm:text-xs/6">
        <Badge color={change.startsWith("+") ? "lime" : "pink"}>{change}</Badge>{" "}
        <span className="text-zinc-500">from last week</span>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const rawdata = getData();
  const historicalSortedData = rawdata.history.sort((a, b) => {
    return a.date.getTime() - b.date.getTime();
  });
  const predictionSortedData = rawdata.prediction.sort((a, b) => {
    return a.date.getTime() - b.date.getTime();
  });

  const historicalSum = historicalSortedData.reduce(
    (acc, { solar }) => {
      acc.solar += solar;
      return acc;
    },
    { solar: 0 }
  );

  const predictionSum = predictionSortedData.reduce(
    (acc, { solar }) => {
      acc.solar += solar;
      return acc;
    },
    { solar: 0 }
  );

  return (
    <>
      <Heading>Energy Dashboard</Heading>
      <div className="mt-8 flex items-end justify-between">
        <Subheading>Total generated</Subheading>
      </div>
      <div className="mt-3 grid gap-8 sm:grid-cols-1 xl:grid-cols-3">
        <Stat
          title="Power produced last 24h"
          value={historicalSum.solar.toFixed(4).toString()}
          change={"+" + (100 * Math.random()).toFixed(2).toString()}
        />
        <Stat
          title="Est. power produced next 24h"
          value={predictionSum.solar.toFixed(4).toString()}
          change={"+" + (100 * Math.random()).toFixed(2).toString()}
        />
      </div>

      <Subheading>Chart</Subheading>

      <LineChart width={1000} height={400} data={historicalSortedData}>
        <CartesianGrid stroke="#ccc" />
        <Line type="monotone" dataKey="solar" stroke="#c7c92a" />
        <Tooltip />
        <XAxis />
        <YAxis />
      </LineChart>

      <Subheading className="mt-14">Energy generated last 24h</Subheading>
      <Table className="mt-4 [--gutter:theme(spacing.6)] lg:[--gutter:theme(spacing.10)]">
        <TableHead>
          <TableRow>
            <TableHeader>Timestamp</TableHeader>
            <TableHeader>Power produced</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {historicalSortedData.map((dataset) => (
            <TableRow
              key={dataset.date.toISOString()}
              title={`Energy production for ${dataset.date}`}
            >
              <TableCell>{dataset.date.toString()}</TableCell>
              <TableCell>{dataset.solar} kwh</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}
