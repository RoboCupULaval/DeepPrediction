#include "protobuf/ssl_referee.pb.h"
#include "protobuf/messages_robocup_ssl_wrapper.pb.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <cstring>
#include <stdint.h>
#include <endian.h>

#include <google/protobuf/util/json_util.h>

struct FileHeader
{
    char name[12]; // SSL_LOG_FILE
    int32_t version; // Default file format is version 1
};

const char* DEFAULT_FILE_HEADER_NAME = "SSL_LOG_FILE";
const int32_t DEFAULT_FILE_VERSION = 1;

struct DataHeader
{
    int64_t timestamp; // Timestamp in ns
    int32_t messageType; // Message type
    int32_t messageSize; // Size of protobuf message in bytes
};

enum MessageType
{
    MESSAGE_BLANK = 0,
    MESSAGE_UNKNOWN = 1,
    MESSAGE_SSL_VISION_2010 = 2,
    MESSAGE_SSL_REFBOX_2013 = 3
};

std::string getJson(const google::protobuf::Message &packet);

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        std::cout << "No input file name specified!" << std::endl;
        std::cout << "Please run \"examplereader <log file>\"." << std::endl;

        return -1;
    }

    const char *filename = argv[1];

    std::ifstream in(filename, std::ios_base::in | std::ios_base::binary);
    std::ofstream output("output.json", std::ios::out | std::ios::trunc);

    if (!in.is_open())
    {
        std::cerr << "Error opening log file \"" << filename << "\"!" << std::endl;
    }

    if (!output)
    {
        std::cerr << "Error opening output file" << std::endl;
    }

    FileHeader fileHeader;
    in.read((char*) &fileHeader, sizeof(fileHeader));
    // Log data is stored big endian, convert to host byte order
    fileHeader.version = be32toh(fileHeader.version);

    if (strncmp(fileHeader.name, DEFAULT_FILE_HEADER_NAME, sizeof(fileHeader.name)) == 0)
    {
        std::cout << "File format version " << fileHeader.version << " detected." << std::endl;

        if (fileHeader.version == DEFAULT_FILE_VERSION)
        {
            unsigned long refereePackets = 0;
            unsigned long visionPackets = 0;
            bool firstTime = true;

            while (!in.eof())
            {

                if ((refereePackets + visionPackets) % 10000 == 0)
                {
                    std::cout << (refereePackets + visionPackets) << " packets read" << std::endl;
                }

                DataHeader dataHeader;
                in.read((char*) &dataHeader, sizeof(dataHeader));
                // Log data is stored big endian, convert to host byte order
                dataHeader.timestamp = be64toh(dataHeader.timestamp);
                dataHeader.messageType = be32toh(dataHeader.messageType);
                dataHeader.messageSize = be32toh(dataHeader.messageSize);

                if (dataHeader.messageSize > 0)
                {

                    char* data = new char[dataHeader.messageSize];

                    in.read(data, dataHeader.messageSize);

                    if (firstTime)
                    {
                        output << "{" << std::endl
                               << "\"packets\": [" << std::endl;
                        firstTime = false;
                    }
                    else
                    {
                        output << "," << std::endl;
                    }

                    output << "{" << std::endl
                           << "\"timestamp\": " << dataHeader.timestamp << "," << std::endl
                           << "\"message_type\": " << dataHeader.messageType << std::endl
                           << "\"message_size\": " << dataHeader.messageSize << std::endl;

                    if (dataHeader.messageType == MESSAGE_SSL_VISION_2010)
                    {
                        SSL_WrapperPacket packet;
                        if (packet.ParseFromArray(data, dataHeader.messageSize))
                        {
                            visionPackets++;

                            output << "\"message\": " << getJson(packet);

                        }
                        else
                        {
                            std::cerr << "Error parsing vision packet!" << std::endl;
                        }
                    }
                    else if (dataHeader.messageType == MESSAGE_SSL_REFBOX_2013)
                    {
                        SSL_Referee packet;
                        if (packet.ParseFromArray(data, dataHeader.messageSize))
                        {
                            refereePackets++;

                            output << "\"message\": " << getJson(packet);

                        }
                        else
                        {
                            std::cerr << "Error parsing vision packet!" << std::endl;
                        }
                    }
                    output << "}";
                    delete data;
                }
            }
            output << "]}" << std::endl;
        }
    }
    else
    {
        std::cerr << "Error log file is unsupported or corrupted!" << std::endl;
    }
    output.close();
    return 0;
}

std::string getJson(const google::protobuf::Message &packet)
{
    std::string json_string;
    google::protobuf::util::JsonPrintOptions options;
    options.add_whitespace = true;
    options.always_print_primitive_fields = true;
    options.preserve_proto_field_names = true;
    MessageToJsonString(packet, &json_string, options);
    return json_string;
}

